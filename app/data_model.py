import asyncio
from typing import Callable, Dict, Any, List, Optional
from collections import defaultdict
from pydantic import BaseModel, Field


class DataInfo(BaseModel):
    # 문서정보 (입력 데이터)
    doc_input: str
    collection: Optional[List[str]] = None
    collection_id: str
    collection_name: str
    collection_memo: str
    user_id: str

    # 처리된 데이터 (갱신 대상) - None으로 초기화하여 갱신 여부 추적
    doc_summarized: Optional[List[str]] = None
    doc_summarized_new: Optional[str] = None
    doc_input_question: Optional[List[str]] = None
    collection_question: Optional[List[str]] = None
    doc_retrieved: Optional[List[str]] = None
    collection_retrieved: Optional[List[str]] = None

    # 동시성 제어를 위한 세밀한 락 시스템
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, **data):
        super().__init__(**data)
        # 필드별 개별 락 생성 (세밀한 동시성 제어)
        object.__setattr__(self, '_field_locks', defaultdict(asyncio.Lock))
        # 전역 락 (필요시에만 사용)
        object.__setattr__(self, '_global_lock', asyncio.Lock())

    async def update(self, process_tasks: List[Callable]):
        """비동기적으로 처리 작업들을 스케쥴링 (최적화된 동시성)"""
        from app import scheduler  # 순환 import 방지를 위해 함수 내부에서 import
        # scheduler에게 자체 락 시스템을 제공하여 의존성에 따른 선택적 락킹
        await scheduler.scheduler(process_tasks, self, self._field_locks)
    
    def _get_processed_fields(self) -> List[str]:
        """기본값이 None인 필드들을 자동으로 감지하여 반환"""
        return [
            field_name for field_name, field_info in self.__class__.model_fields.items()
            if field_info.default is None
        ]
    
    async def is_data_updated(self) -> Dict[str, bool]:
        """각 데이터 필드의 갱신 여부를 확인 (비동기 안전)"""
        # 일관된 스냅샷을 위해 전역 락 사용
        async with self._global_lock:
            return {
                field: getattr(self, field) is not None 
                for field in self._get_processed_fields()
            }
    
    async def get_updated_fields(self) -> Dict[str, Any]:
        """갱신된 필드들만 반환 (None이 아닌 값들, 비동기 안전)"""
        async with self._global_lock:
            return {
                field: getattr(self, field) 
                for field in self._get_processed_fields() 
                if getattr(self, field) is not None
            }
    
    async def safe_update_field(self, field_name: str, value: Any) -> bool:
        """개별 필드를 안전하게 업데이트 (세밀한 락 사용)"""
        if field_name not in self._get_processed_fields():
            return False
        
        # 해당 필드만 락킹하여 다른 필드와 동시 수정 가능
        async with self._field_locks[field_name]:
            setattr(self, field_name, value)
            return True
    
    async def parallel_update_fields(self, field_updates: Dict[str, Any]) -> Dict[str, bool]:
        """여러 필드를 병렬로 안전하게 업데이트"""
        async def update_single_field(field_name: str, value: Any) -> tuple[str, bool]:
            success = await self.safe_update_field(field_name, value)
            return field_name, success
        
        # 각 필드별로 독립적인 락을 사용하여 병렬 처리
        tasks = [
            update_single_field(field, value) 
            for field, value in field_updates.items()
        ]
        
        results = await asyncio.gather(*tasks)
        return dict(results)
    
    def get_field_lock(self, field_name: str) -> asyncio.Lock:
        """특정 필드의 락을 반환 (외부 모듈에서 사용)"""
        return self._field_locks[field_name]


class ProcessRequest(BaseModel):
    """처리 요청을 위한 모델"""
    doc_input: str
    #collection: List[str]
    collection_id: str
    collection_name: str
    collection_memo: str
    user_id: str


class Question(BaseModel):
    """생성된 질문을 나타내는 모델"""
    question: str = Field(description="문서 내용을 기반으로 생성된 질문")
    category: str = Field(description="질문의 카테고리 (예: 기본정보, 세부사항, 분석, 적용 등)")
    difficulty: str = Field(description="질문의 난이도 (easy, medium, hard)")

class QuestionsResponse(BaseModel):
    """여러 질문들을 담는 응답 모델"""
    questions: List[Question] = Field(description="생성된 질문들의 리스트", min_items=3, max_items=10)
    total_count: int = Field(description="생성된 총 질문 수")
