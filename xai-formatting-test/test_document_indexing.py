"""
실제 문서 인덱싱 구조화된 출력 테스트
"""
import asyncio
from xai_client import create_client
from data_models import QuestionsResponse


# 테스트용 문서 데이터
SAMPLE_DOCUMENT = """
[8월22일] 구글이 돈 안 되는 픽셀폰을 계속 내놓는 이유는..."제미나이 위한 것"

구글이 20일(현지시간) 미국 뉴욕에서 '메이드 바이 구글'이라는 행사를 열고 신형 '픽셀폰 10'을 공개했습니다. 
픽셀폰은 존재감이 별로 없습니다. 미국이나 일본에는 일부 마니아층도 있는 것으로 알려졌지만, 국내를 비롯해 상당수 국가에는 판매되지 않습니다. 
판매량도 미미합니다. IDC 데이터에 따르면, 상반기 글로벌 휴대폰 시장 점유율은 0.3%에 불과합니다.

구글도 이 점을 잘 알고 있습니다. 픽셀폰을 총괄하는 닉 오스터로 구글 부사장은 "픽셀이 결코 거대 기업이 될 수는 없을 것"이라고 인정하고 있습니다.

그런데 구글은 왜 픽셀폰을 2016년부터 10년째 제작하고 있을까요. 이에 대해 행사 직후 진행한 CNBC, 블룸버그 등과의 인터뷰에서 이유를 밝혔습니다.

결론부터 말하자면, 픽셀폰으로 큰돈을 벌겠다는 의도가 아니라는 것입니다. 소프트웨어와 인공지능(AI) 측면에서 안드로이드가 제공하는 최고의 기능을 선보이는 것이 목표라고 합니다.

안드로이드 체제를 운영하는 입장에서, 이를 통해 삼성이나 샤오미와 같은 글로벌 제조업체에 기술을 제공하기 전에 테스트 장치 역할을 한다는 내용입니다.
"""

COLLECTION_MEMO = """
- 구글 픽셀폰의 진짜 목적: 수익성보다는 안드로이드 파트너들을 위한 레퍼런스 기기 역할과 AI 기능 테스트 장치로 활용하는 것이 주된 목표
- 제미나이 AI 확산 전략: 픽셀폰을 통해 제미나이 AI를 자연스럽게 일상 기능에 통합하여 모바일에서 챗GPT 대비 우위를 확보하려는 전략
- 안드로이드 생태계 활용: 전 세계 30억 대의 안드로이드 기기를 통해 제미나이 사용자 기반을 확대하고 플라이휠 효과를 창출
- 장기적 관점의 사업: 단기 수익성보다는 구글의 다양한 영역에서 중요한 역할을 하는 장기적 투자로 픽셀폰 사업을 지속할 예정
"""


def create_document_indexing_prompt(doc_input: str, memopad: str) -> str:
    """문서 인덱싱을 위한 시스템 프롬프트 생성"""
    return f"""You are a librarian who guides a smart, bright and curious student. Please think of questions that can be solved through this document below.
이 문서를 보고 있는 사람이 작성중인 메모의 편린을 제공할게. 질문 생성에 참고해.
This is a pre-processing for document Dense Passage Retrieval search/recommendation.

Generate 5-8 diverse questions based on the document content. Each question should:
1. Be answerable using information from the document
2. Cover different aspects (basic info, details, analysis, application)
3. Have varying difficulty levels
4. Be relevant to the user's memo context when available

The questions will be used for document retrieval and recommendation, so make them comprehensive and searchable.

[Document]
{doc_input}

[Memo]
{memopad}"""


async def test_document_indexing_structured():
    """문서 인덱싱 구조화된 출력 테스트"""
    print("🧪 문서 인덱싱 구조화된 출력 테스트 시작...")
    
    client = create_client()
    
    system_prompt = create_document_indexing_prompt(SAMPLE_DOCUMENT, COLLECTION_MEMO)
    
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
        
        print(f"✅ 성공! 구조화된 문서 인덱싱 결과:")
        print(f"   총 질문 수: {result.total_count}")
        print(f"   질문 리스트:")
        
        for i, question in enumerate(result.questions, 1):
            print(f"      {i}. 질문: {question.question}")
            print(f"         카테고리: {question.category}")
            print(f"         난이도: {question.difficulty}")
            print()
        
        print(f"   반환 타입: {type(result)}")
        
        # JSON 형태로도 출력
        print("\n📄 JSON 형태 출력:")
        questions_dict = {
            "questions": [q.model_dump() for q in result.questions],
            "total_count": result.total_count
        }
        print(questions_dict)
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_document_indexing_fallback():
    """기존 방식 (텍스트 출력) 테스트 - 비교용"""
    print("\n🧪 기존 방식 (텍스트 출력) 테스트 시작...")
    
    client = create_client()
    
    system_prompt = f"""You are a librarian who guides a smart, bright and curious student. Please think of questions that can be solved through this document below.
이 문서를 보고 있는 사람이 작성중인 메모의 편린을 제공할게. 질문 생성에 참고해.
This is a pre-processing for document Dense Passage Retrieval search/recommendation.

Generate 5-8 diverse questions based on the document content. Each question should:
1. Be answerable using information from the document
2. Cover different aspects (basic info, details, analysis, application)
3. Have varying difficulty levels
4. Be relevant to the user's memo context when available

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
{SAMPLE_DOCUMENT}

[Memo]
{COLLECTION_MEMO}"""
    
    prompt = "위 문서를 기반으로 검색과 추천에 유용한 질문들을 생성해주세요."
    
    try:
        result = await client.generate_text(
            prompt=prompt,
            system_prompt=system_prompt
        )
        
        print(f"✅ 성공! 텍스트 응답:")
        print(f"   내용: {result}")
        print(f"   타입: {type(result)}")
        
        # 수동 JSON 파싱 시도
        try:
            import json
            import re
            
            # JSON 추출 시도
            cleaned_json = result.replace("```json", "").replace("```", "").strip()
            cleaned_json = re.sub(r'^[^{[]*', '', cleaned_json)
            cleaned_json = re.sub(r'[^}\]]*$', '', cleaned_json)
            
            parsed_result = json.loads(cleaned_json)
            print(f"\n📄 파싱된 JSON:")
            print(f"   총 질문 수: {parsed_result.get('total_count', 0)}")
            print(f"   질문 수: {len(parsed_result.get('questions', []))}")
            
        except Exception as parse_error:
            print(f"⚠️ JSON 파싱 실패: {parse_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False


async def main():
    """모든 문서 인덱싱 테스트 실행"""
    print("🚀 xAI 문서 인덱싱 구조화된 출력 테스트 시작\n")
    
    tests = [
        ("구조화된 문서 인덱싱", test_document_indexing_structured),
        ("기존 방식 (비교용)", test_document_indexing_fallback),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"테스트: {test_name}")
        print('='*60)
        
        success = await test_func()
        results.append((test_name, success))
    
    # 결과 요약
    print(f"\n{'='*60}")
    print("테스트 결과 요약")
    print('='*60)
    
    for test_name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    print(f"\n총 {total_tests}개 테스트 중 {passed_tests}개 성공")
    
    if passed_tests == total_tests:
        print("🎉 모든 테스트가 성공했습니다!")
        print("\n✨ 구조화된 출력이 제대로 작동합니다!")
        print("   - JSON 스키마 자동 생성 ✅")
        print("   - Pydantic 모델 검증 ✅") 
        print("   - 타입 안전성 ✅")
    else:
        print(f"⚠️  {total_tests - passed_tests}개 테스트가 실패했습니다.")


if __name__ == "__main__":
    asyncio.run(main())