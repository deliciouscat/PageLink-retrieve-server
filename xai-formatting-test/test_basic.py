"""
기본 xAI 구조화된 출력 테스트
"""
import asyncio
from datetime import datetime
from xai_client import create_client
from data_models import SimpleResponse, TestUserProfile


async def test_simple_structured_output():
    """간단한 구조화된 출력 테스트"""
    print("🧪 간단한 구조화된 출력 테스트 시작...")
    
    client = create_client()
    
    prompt = "안녕하세요! 현재 시간을 알려주세요."
    system_prompt = "현재 시간과 함께 친근한 인사말을 해주세요. 신뢰도는 0.9로 설정하세요."
    
    try:
        result = await client.generate_structured(
            prompt=prompt,
            output_type=SimpleResponse,
            system_prompt=system_prompt
        )
        
        print(f"✅ 성공! 구조화된 응답:")
        print(f"   메시지: {result.message}")
        print(f"   시간: {result.timestamp}")
        print(f"   신뢰도: {result.confidence}")
        print(f"   타입: {type(result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False


async def test_user_profile_extraction():
    """사용자 프로필 추출 테스트"""
    print("\n🧪 사용자 프로필 추출 테스트 시작...")
    
    client = create_client()
    
    prompt = """
    다음 정보에서 사용자 프로필을 추출해주세요:
    "안녕하세요, 저는 김철수이고 28세입니다. 서울에 살고 있으며, 
    프로그래밍, 독서, 영화감상을 좋아합니다."
    """
    
    system_prompt = "주어진 텍스트에서 사용자 정보를 정확히 추출해주세요."
    
    try:
        result = await client.generate_structured(
            prompt=prompt,
            output_type=TestUserProfile,
            system_prompt=system_prompt
        )
        
        print(f"✅ 성공! 추출된 프로필:")
        print(f"   이름: {result.name}")
        print(f"   나이: {result.age}")
        print(f"   위치: {result.location}")
        print(f"   관심사: {result.interests}")
        print(f"   타입: {type(result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False


async def test_text_generation():
    """기본 텍스트 생성 테스트 (비교용)"""
    print("\n🧪 기본 텍스트 생성 테스트 시작...")
    
    client = create_client()
    
    prompt = "xAI Grok 모델에 대해 간단히 설명해주세요."
    system_prompt = "간결하고 정확한 정보를 제공하는 어시스턴트입니다."
    
    try:
        result = await client.generate_text(
            prompt=prompt,
            system_prompt=system_prompt
        )
        
        print(f"✅ 성공! 텍스트 응답:")
        print(f"   내용: {result}")
        print(f"   타입: {type(result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False


async def main():
    """모든 기본 테스트 실행"""
    print("🚀 xAI 구조화된 출력 기본 테스트 시작\n")
    
    tests = [
        ("기본 텍스트 생성", test_text_generation),
        ("간단한 구조화된 출력", test_simple_structured_output),
        ("사용자 프로필 추출", test_user_profile_extraction),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"테스트: {test_name}")
        print('='*50)
        
        success = await test_func()
        results.append((test_name, success))
    
    # 결과 요약
    print(f"\n{'='*50}")
    print("테스트 결과 요약")
    print('='*50)
    
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


if __name__ == "__main__":
    asyncio.run(main())