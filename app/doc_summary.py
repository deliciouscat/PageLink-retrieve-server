"""
문서 요약 모듈 - 더미 구현
"""
import asyncio
import random


async def doc_summary(data_instance):
    """
    문서 요약 함수 (더미 구현)
    doc_input을 받아서 요약본을 생성
    """
    print(f"📝 [doc_summary] 시작 - User: {data_instance.user_id}")
    
    # 1-2초 딜레이 시뮬레이션
    delay = random.uniform(1.0, 2.0)
    await asyncio.sleep(delay)
    
    # 더미 요약 결과 생성
    summary = f"문서 요약: {data_instance.doc_input[:50]}... (요약 완료)"
    
    print(f"✅ [doc_summary] 완료 ({delay:.1f}초) - User: {data_instance.user_id}")
    return summary