# 비동기 처리
`main.py`의 `process_tasks`를 중첩 리스트 구조로 정의한다.
예시:
```
process_tasks = [
        [doc_summary, expand_collection_query, search_docs], 
        doc_indexing
        ]
```
-> doc_summary ~ search_docs는 순차적으로 수행. doc_indexing은 이와 병렬적으로 수행.

`scheduler.py`의 field_mapping 수정해서 함수 별 출력값 매핑
```
field_mapping = {
        'doc_summary': 'doc_summarized_new',
        'doc_indexing': 'doc_input_question', 
        'expand_collection_query': 'collection_question',
        'search_docs': 'doc_retrieved'
    }
```


## 테스트 방법
### 터미널 1: Service Server 시뮬레이터
`uv run input_sample/simple_simulator.py`

### 터미널 2: Retrieve Server  
`uv run main.py`

### 터미널 3: 클라이언트 테스트
`uv run input_sample/simple_client.py --sample 1`
`uv run input_sample/simple_client.py --sample 2`