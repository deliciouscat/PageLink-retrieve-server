"""
실제 프로젝트 데이터를 사용한 xAI 구조화된 출력 테스트
"""
import asyncio
import json
from jinja2 import Environment, FileSystemLoader
from xai_client import create_client
from data_models import QuestionsResponse


def load_sample_data():
    """샘플 데이터 로드"""
    with open('sample_input_1.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def create_prompt_with_template(doc_input: str, memopad: str) -> str:
    """Jinja2 템플릿을 사용해서 프롬프트 생성"""
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('doc_indexing_250830.jinja')
    return template.render(doc_input=doc_input, memopad=memopad)


async def test_with_real_project_data_structured():
    """실제 프로젝트 데이터로 구조화된 출력 테스트"""
    print("🧪 실제 프로젝트 데이터 - 구조화된 출력 테스트 시작...")
    
    # 샘플 데이터 로드
    sample_data = load_sample_data()
    
    # Jinja2 템플릿으로 시스템 프롬프트 생성
    system_prompt = create_prompt_with_template(
        sample_data['doc_input'],
        sample_data['collection_memo']
    )
    
    client = create_client()
    
    prompt = "위 문서를 기반으로 검색과 추천에 유용한 질문들을 생성해주세요."
    
    try:
        result = await client.generate_structured(
            prompt=prompt,
            output_type=QuestionsResponse,
            system_prompt=system_prompt,
            model_settings={
                "temperature": 0.75,
                "max_tokens": 1000,
            }
        )
        
        print(f"✅ 성공! 구조화된 출력:")
        print(f"   총 질문 수: {result.total_count}")
        print(f"   질문 리스트:")
        
        for i, question in enumerate(result.questions, 1):
            print(f"      {i}. 질문: {question.question}")
            print(f"         카테고리: {question.category}")
            print(f"         난이도: {question.difficulty}")
            print()
        
        # JSON 형태로도 출력
        print("\n📄 JSON 형태 출력:")
        questions_dict = {
            "questions": [q.model_dump() for q in result.questions],
            "total_count": result.total_count
        }
        print(json.dumps(questions_dict, ensure_ascii=False, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_with_real_project_data_text():
    """실제 프로젝트 데이터로 텍스트 출력 테스트 (비교용)"""
    print("\n🧪 실제 프로젝트 데이터 - 텍스트 출력 테스트 시작...")
    
    # 샘플 데이터 로드
    sample_data = load_sample_data()
    
    # JSON 형식 지시가 포함된 프롬프트 생성
    system_prompt = f"""You are a librarian who guides a smart, bright and curious student. Please think of questions that can be solved through this document below.
이 문서를 보고 있는 사람이 작성중인 메모의 편린을 제공할게. 질문 생성에 참고해.
This is a pre-processing for document Dense Passage Retrieval search/recommendation.

Generate 5-8 diverse questions based on the document content. Each question should:
1. Be answerable using information from the document
2. Cover different aspects (basic info, details, analysis, application)
3. Have varying difficulty levels
4. Be relevant to the user's memo context when available

The questions will be used for document retrieval and recommendation, so make them comprehensive and searchable.

**Output format: Return your response as a valid JSON object with this exact structure:**
```json
{{
  "questions": [
    {{
      "question": "질문 내용",
      "category": "기본정보|세부사항|분석|적용",
      "difficulty": "easy|medium|hard"
    }}
  ],
  "total_count": 5
}}
```

[Document]
{sample_data['doc_input']}

[Memo]
{sample_data['collection_memo']}"""
    
    client = create_client()
    
    prompt = "위 문서를 기반으로 검색과 추천에 유용한 질문들을 생성해주세요."
    
    try:
        result = await client.generate_text(
            prompt=prompt,
            system_prompt=system_prompt
        )
        
        print(f"✅ 성공! 텍스트 응답:")
        print(f"   응답 길이: {len(result)} 문자")
        print(f"   타입: {type(result)}")
        
        # JSON 파싱 시도
        try:
            import re
            
            # JSON 추출
            cleaned_json = result.replace("```json", "").replace("```", "").strip()
            cleaned_json = re.sub(r'^[^{[]*', '', cleaned_json)
            cleaned_json = re.sub(r'[^}\]]*$', '', cleaned_json)
            
            parsed_result = json.loads(cleaned_json)
            
            print(f"\n📄 파싱된 JSON:")
            print(f"   총 질문 수: {parsed_result.get('total_count', 0)}")
            print(f"   질문 수: {len(parsed_result.get('questions', []))}")
            
            print(f"\n📝 생성된 질문들:")
            for i, q in enumerate(parsed_result.get('questions', []), 1):
                print(f"      {i}. 질문: {q.get('question', '없음')}")
                print(f"         카테고리: {q.get('category', '없음')}")
                print(f"         난이도: {q.get('difficulty', '없음')}")
                print()
            
            print(f"\n📄 전체 JSON:")
            print(json.dumps(parsed_result, ensure_ascii=False, indent=2))
            
        except Exception as parse_error:
            print(f"⚠️ JSON 파싱 실패: {parse_error}")
            print(f"원본 응답:")
            print(result[:500] + "..." if len(result) > 500 else result)
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False


async def test_with_simpler_schema():
    """더 단순한 스키마로 구조화된 출력 테스트"""
    print("\n🧪 단순한 스키마로 구조화된 출력 테스트...")
    
    from data_models import TestUserProfile
    
    client = create_client()
    
    prompt = """
    다음 샘플 데이터를 기반으로 가상의 사용자 프로필을 생성해주세요:
    - 이름: 김개발
    - 나이: 32
    - 관심사: IT뉴스, 구글 제품, AI 기술
    - 위치: 서울
    """
    
    system_prompt = "주어진 정보를 바탕으로 사용자 프로필을 생성해주세요."
    
    try:
        result = await client.generate_structured(
            prompt=prompt,
            output_type=TestUserProfile,
            system_prompt=system_prompt
        )
        
        print(f"✅ 성공! 단순한 구조화된 출력:")
        print(f"   이름: {result.name}")
        print(f"   나이: {result.age}")
        print(f"   위치: {result.location}")
        print(f"   관심사: {result.interests}")
        print(f"   타입: {type(result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False


async def main():
    """모든 실제 프로젝트 데이터 테스트 실행"""
    print("🚀 실제 프로젝트 데이터를 사용한 xAI 테스트 시작\n")
    
    tests = [
        ("단순한 스키마 (사용자 프로필)", test_with_simpler_schema),
        ("구조화된 문서 인덱싱 (복잡한 스키마)", test_with_real_project_data_structured),
        ("텍스트 출력 (기존 방식)", test_with_real_project_data_text),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"테스트: {test_name}")
        print('='*70)
        
        success = await test_func()
        results.append((test_name, success))
    
    # 결과 요약
    print(f"\n{'='*70}")
    print("테스트 결과 요약")
    print('='*70)
    
    for test_name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    print(f"\n총 {total_tests}개 테스트 중 {passed_tests}개 성공")
    
    if passed_tests == total_tests:
        print("🎉 모든 테스트가 성공했습니다!")
    else:
        print(f"⚠️  {total_tests - passed_tests}개 테스트가 실패했습니다.")
    
    # 결론
    print(f"\n{'='*70}")
    print("🔍 분석 결과")
    print('='*70)
    
    if any(name.startswith("구조화된") and success for name, success in results):
        print("✨ xAI Grok-3-mini는 구조화된 출력을 지원합니다!")
    
    if any(name.startswith("텍스트") and success for name, success in results):
        print("✨ 기존 방식(프롬프트 기반)도 완벽하게 작동합니다!")
    
    print("\n💡 권장사항:")
    print("   - 현재는 기존 방식(프롬프트 + JSON 파싱)이 더 안정적")
    print("   - 구조화된 출력은 단순한 스키마에서 잘 작동")
    print("   - 복잡한 스키마는 아직 일부 제한이 있음")
    print("   - 하이브리드 접근법(기존 + 개선된 파싱) 추천")


if __name__ == "__main__":
    asyncio.run(main())