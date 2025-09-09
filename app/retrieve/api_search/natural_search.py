import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

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

def from_openrouter(query: str, advanced: bool = False) -> SearchResult:
    model = "perplexity/sonar"
    if advanced: model += ":online"
    
    completion = client.chat.completions.create(
        extra_body={},
        model=model,
        max_tokens=1,
        messages=[
            {
            "role": "user",
            "content": [
                    {
                        "type": "text",
                        "text": query
                    },
                ]
            }
        ]
    )
    annotations = completion.choices[0].message.annotations
    urls = [a.url_citation.url for a in annotations]
    return SearchResult(
        urls=urls,
        query=query,
        model=model,
        advanced=advanced,
        total_results=len(urls)
    )

"""
Output result example:
SearchResult(
    urls=[
        'https://www.kimstanleyrobinson.info/content/martian-government',
        'https://beca-alliance.com/members/anton-vincent/',
        'https://www.lawonmars.com/government-of-mars',
        'https://www.comparably.com/companies/mars/executive-team',
        'http://www.rcmun.org/martian-government.html'
    ],
    query="Who is the president of Mars?",
    model="perplexity/sonar",
    advanced=False,
    total_results=5
)
"""