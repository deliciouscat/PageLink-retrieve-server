"""
데이터베이스 모듈 - 더미 구현
"""
import asyncio


async def send_to_db(data_instance, db_config):
    """
    데이터베이스에 저장하는 더미 함수
    """
    print(f"💾 [DB] 저장 시작 - User: {data_instance.user_id}")
    
    # 짧은 딜레이 시뮬레이션
    await asyncio.sleep(0.5)
    
    # 저장할 데이터 정보 출력
    for db_name, fields in db_config.items():
        print(f"   📁 {db_name}: {fields}")
    
    print(f"✅ [DB] 저장 완료 - User: {data_instance.user_id}")
    return True