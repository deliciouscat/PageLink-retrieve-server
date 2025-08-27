import asyncio
from typing import List, Union, Callable, Dict, Any
from collections import defaultdict


async def scheduler(
    process_tasks: List[Union[Callable, List]], 
    data_instance, 
    lock_manager: Dict[str, asyncio.Lock] = None
) -> None:
    """
    비동기 처리 스케쥴링을 담당하는 함수
    
    Args:
        process_tasks: 처리할 작업들의 리스트
                    - Callable: 독립적으로 실행할 함수
                    - List[Callable]: 순차적으로 실행할 함수들의 체인
        data_instance: DataInfo 인스턴스 (처리 대상)
        lock_manager: 필드별 락 매니저 (동시성 제어용)
    
    Example:
        process_tasks = [
            [doc_summary, expand_collection_query, search_docs],  # 순차 실행
            doc_indexing  # 독립 실행
        ]
    """
    if lock_manager is None:
        lock_manager = defaultdict(asyncio.Lock)
    
    # 독립 작업과 순차 작업 분리
    independent_tasks = []
    sequential_chains = []
    
    for task in process_tasks:
        if callable(task):
            # 단일 함수 -> 독립 작업
            independent_tasks.append(task)
        elif isinstance(task, list):
            # 함수 리스트 -> 순차 작업 체인
            sequential_chains.append(task)
        else:
            raise ValueError(f"지원하지 않는 작업 타입: {type(task)}")
    
    # 모든 작업을 비동기로 시작
    all_tasks = []
    
    # 독립 작업들을 병렬로 실행
    for task in independent_tasks:
        all_tasks.append(_execute_single_task(task, data_instance, lock_manager))
    
    # 순차 작업 체인들을 병렬로 실행 (각 체인 내부는 순차)
    for chain in sequential_chains:
        all_tasks.append(_execute_sequential_chain(chain, data_instance, lock_manager))
    
    # 모든 작업이 완료될 때까지 대기
    if all_tasks:
        await asyncio.gather(*all_tasks)


async def _execute_single_task(
    task: Callable, 
    data_instance, 
    lock_manager: Dict[str, asyncio.Lock]
) -> None:
    """단일 작업을 비동기로 실행"""
    try:
        # 작업 실행 (필요에 따라 락 사용)
        result = await task(data_instance)
        
        # 결과가 있으면 data_instance에 반영
        if result is not None:
            await _update_data_instance(data_instance, task.__name__, result, lock_manager)
            
    except Exception as e:
        print(f"작업 '{task.__name__}' 실행 중 오류 발생: {e}")
        raise


async def _execute_sequential_chain(
    chain: List[Callable], 
    data_instance, 
    lock_manager: Dict[str, asyncio.Lock]
) -> None:
    """순차 작업 체인을 실행 (체인 내부는 순차, 다른 체인과는 병렬)"""
    try:
        for task in chain:
            # 체인 내에서는 순차적으로 실행
            result = await task(data_instance)
            
            # 결과가 있으면 data_instance에 반영
            if result is not None:
                await _update_data_instance(data_instance, task.__name__, result, lock_manager)
                
    except Exception as e:
        print(f"순차 체인 실행 중 오류 발생: {e}")
        raise


async def _update_data_instance(
    data_instance, 
    task_name: str, 
    result: Any, 
    lock_manager: Dict[str, asyncio.Lock]
) -> None:
    """
    작업 결과를 data_instance에 안전하게 업데이트
    
    각 함수명에 따라 적절한 필드에 결과를 저장
    """
    # 함수명과 필드명 매핑
    field_mapping = {
        'doc_summary': 'doc_summarized_new',
        'doc_indexing': 'doc_input_question', 
        'expand_collection_query': 'collection_question',
        'search_docs': 'doc_retrieved'
    }
    
    field_name = field_mapping.get(task_name)
    if field_name:
        # 해당 필드의 락을 사용하여 안전하게 업데이트
        async with lock_manager[field_name]:
            setattr(data_instance, field_name, result)
    else:
        print(f"알 수 없는 작업명: {task_name}")


# 편의를 위한 기본 스케쥴러 함수 (기존 호출 방식 유지)
async def default_scheduler(process_tasks: List, data_instance) -> None:
    """기본 스케쥴러 - 기존 main.py의 호출 방식과 호환"""
    await scheduler(process_tasks, data_instance)