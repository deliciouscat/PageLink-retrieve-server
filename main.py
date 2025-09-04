import asyncio
import uvicorn
import logging
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from app.data_model import DataInfo, ProcessRequest
from app.db import send_to_db
from app import scheduler   # 의존성을 고려한 비동기 처리 스케쥴링
from app import (
    doc_summary,  # `doc_summarided_new` 갱신
    doc_indexing,  # `doc_input_question` 갱신
    expand_collection_query,  # `collection_question` 갱신
    search_docs,  # `doc_retrieved` 갱신
    )
load_dotenv()

app = FastAPI()

async def process_user_data(request: ProcessRequest) -> DataInfo:
    """단일 유저의 데이터를 비동기적으로 처리"""
    # 1. Service server에서 정보 불러오기(parsed 웹페이지, user_id, collection_id)
    # 2. user_info DB에서 호출
    # 3. 문서 요약
    # 4. 문서 인덱스 생성
    # 5. 질문 쿼리 생성
    # 6. 추천 문서 retrieve
    # 7. User_info DB에 저장
    # 8. IndexPage DB에 저장
    
    # DataInfo 인스턴스 생성 (처리된 데이터는 None으로 초기화)
    data = DataInfo(
        doc_input=request.doc_input,
        #collection=request.collection,
        collection_id=request.collection_id,
        collection_name=request.collection_name,
        collection_memo=request.collection_memo,
        user_id=request.user_id,
        # 처리된 데이터들은 기본값 None으로 자동 초기화됨

        # 임시(나중엔 UserInfo DB에서 불러오게 될 부분)
        doc_summarized=request.doc_summarized,
    )
    
    # User_info에서 데이터 호출
    #await get_user_info(data)

    # 처리 작업들 정의
    process_tasks = [
        [doc_summary, expand_collection_query, search_docs], 
        doc_indexing
        ]
    
    # 비동기 처리 실행
    await scheduler.scheduler(process_tasks, data, data._field_locks)
    
    # DB에 저장
    await send_to_db(data, {
        'user_info': [
            'collection_question', 'doc_retrieved', 'collection_retrieved'
        ],
        'index_page': [
            'doc_summarized_new', 'doc_input_question'
        ],
    })
    #logging.info(f"DB에 저장 완료: \n"
    print(f"DB에 저장 완료: \n"
                #f"user_id={data.user_id}, \n"
                #f"collection_id={data.collection_id}, \n"
                #f"collection_name={data.collection_name}, \n"
                #f"collection_memo={data.collection_memo}, \n"
                f"doc_input_question={data.doc_input_question}, \n"
                f"collection_question={data.collection_question}, \n"
                f"doc_retrieved={data.doc_retrieved}, \n"
                f"collection_retrieved={data.collection_retrieved}, \n"
                f"doc_summarized_new={data.doc_summarized_new}, \n"
                #f"doc_input={data.doc_input}"
                )
    
    return data

@app.post("/process")
async def process_document(request: ProcessRequest):
    """문서 처리 API 엔드포인트 - 여러 유저 요청을 비동기적으로 처리"""
    try:
        result = await process_user_data(request)
        return {"status": "success", "user_id": result.user_id, "message": "처리 완료"}
    except Exception as e:
        logging.error(f"처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"처리 중 오류 발생: {str(e)}")

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy"}

async def main():
    """메인 함수 - 비동기 처리를 위한 진입점"""
    print("PageLink Retrieve Server 시작...")
    # 추가적인 초기화 작업이 있다면 여기에 구현
    pass



if __name__ == "__main__":
    print("PageLink Retrieve Server 시작...")
    uvicorn.run(app, host="0.0.0.0", port=8000)