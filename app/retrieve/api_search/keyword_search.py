import os
from dotenv import load_dotenv
from ddgs import DDGS
from pydantic import BaseModel, Field
from typing import List
load_dotenv()

class SearchResult(BaseModel):
    """자연어 검색 결과를 나타내는 pydantic 모델"""
    urls: List[str] = Field(description="검색 결과로 반환된 URL 목록")
    query: str = Field(description="검색에 사용된 쿼리")
    model: str = Field(description="사용된 AI 모델")
    advanced: bool = Field(description="고급 검색 모드 사용 여부")
    total_results: int = Field(description="반환된 결과 수")

class SearchRequest(BaseModel):
    """검색 요청을 나타내는 pydantic 모델"""
    query: str = Field(description="검색할 쿼리 문자열")
    advanced: bool = Field(default=False, description="고급 검색 모드 사용 여부")

def from_ddgs(query: str, advanced: bool = False) -> SearchResult:
    max_results = 4
    if advanced: max_results = 8

    results = DDGS().text(
        query, 
        max_results=max_results,
        #language="ko",
        )
    urls = [result['body'] for result in results]
    return SearchResult(
        urls=urls,
        query=query,
        model="ddgs",
        advanced=advanced,
        total_results=len(urls)
    )