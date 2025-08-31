# xAI 구조화된 출력 테스트

이 디렉토리는 xAI Grok 모델의 구조화된 출력 기능을 테스트하기 위한 코드들을 포함합니다.

## 설치 및 설정

1. **의존성 설치**
```bash
pip install -r requirements.txt
```

2. **환경 변수 설정**
`env_example.txt`를 참고하여 `.env` 파일을 생성하고 API 키를 설정하세요:
```bash
cp env_example.txt .env
# .env 파일을 열어서 OPENROUTER_API_KEY 설정
```

## 파일 구조

- `data_models.py`: Pydantic 데이터 모델 정의
- `xai_client.py`: xAI API 클라이언트 (pydantic-ai 사용)
- `test_basic.py`: 기본 구조화된 출력 테스트
- `test_document_indexing.py`: 실제 문서 인덱싱 테스트
- `requirements.txt`: 필요한 Python 패키지들

## 테스트 실행

### 1. 기본 테스트 실행
```bash
python test_basic.py
```

이 테스트는 다음을 확인합니다:
- ✅ 기본 텍스트 생성
- ✅ 간단한 구조화된 출력 (`SimpleResponse`)
- ✅ 사용자 프로필 추출 (`TestUserProfile`)

### 2. 문서 인덱싱 테스트 실행
```bash
python test_document_indexing.py
```

이 테스트는 다음을 확인합니다:
- ✅ 실제 문서에서 구조화된 질문 생성 (`QuestionsResponse`)
- ✅ 기존 방식(프롬프트 기반)과 비교

## 주요 기능 테스트

### 구조화된 출력의 장점
1. **자동 JSON 스키마 생성**: Pydantic 모델이 자동으로 JSON 스키마로 변환
2. **타입 안전성**: 응답이 자동으로 Pydantic 객체로 파싱되어 타입 안전성 보장
3. **검증**: 응답이 정의된 스키마에 맞지 않으면 자동으로 오류 발생
4. **편의성**: 수동 JSON 파싱 불필요

### 비교: 기존 방식 vs 구조화된 출력

#### 기존 방식 (프롬프트 기반)
```python
# 프롬프트에 JSON 형식 지시
system_prompt = "Return JSON format: {\"questions\": [...], \"total_count\": 5}"
result = await client.generate_text(prompt, system_prompt)
# 수동 JSON 파싱 필요
parsed = json.loads(result)
```

#### 구조화된 출력 (pydantic-ai)
```python
# Pydantic 모델 정의만으로 충분
result = await client.generate_structured(
    prompt=prompt,
    output_type=QuestionsResponse  # 자동 스키마 생성
)
# result는 이미 QuestionsResponse 객체
```

## 데이터 모델

### QuestionsResponse
문서 인덱싱을 위한 질문 생성 응답:
```python
class QuestionsResponse(BaseModel):
    questions: List[Question]  # 생성된 질문들
    total_count: int          # 총 질문 수
```

### Question
개별 질문 정보:
```python
class Question(BaseModel):
    question: str              # 질문 내용
    category: QuestionCategory # 카테고리 (기본정보/세부사항/분석/적용)
    difficulty: DifficultyLevel # 난이도 (easy/medium/hard)
```

## 예상 결과

성공적으로 실행되면 다음과 같은 결과를 확인할 수 있습니다:

1. **구조화된 응답 자동 생성**
2. **타입 안전성 보장**
3. **JSON 파싱 불필요**
4. **스키마 검증 자동화**

이를 통해 xAI Grok 모델도 OpenAI처럼 구조화된 출력을 완벽하게 지원함을 확인할 수 있습니다.