"""
xAI API 클라이언트 (pydantic-ai 사용)
"""
import os
from typing import Type, TypeVar, Any
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv

# 환경 변수 로드 (프로젝트 루트의 .env 파일에서)
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

T = TypeVar('T', bound=BaseModel)


class XAIClient:
    """xAI API 클라이언트"""
    
    def __init__(self, model_name: str = "x-ai/grok-3-mini"):
        self.model_name = model_name
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY 환경 변수가 설정되지 않았습니다.")
        
        # OpenAI Model with OpenRouter provider 설정
        self.model = OpenAIModel(
            self.model_name,
            provider=OpenRouterProvider(api_key=self.api_key),
        )
    
    async def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        """기본 텍스트 생성"""
        agent = Agent(
            self.model,
            system_prompt=system_prompt or "You are a helpful assistant.",
        )
        
        result = await agent.run(prompt)
        return result.output
    
    async def generate_structured(
        self, 
        prompt: str, 
        output_type: Type[T], 
        system_prompt: str = None,
        model_settings: dict = None
    ) -> T:
        """구조화된 출력 생성"""
        settings = model_settings or {"temperature": 0.7, "max_tokens": 1000}
        
        agent = Agent(
            self.model,
            system_prompt=system_prompt or "You are a helpful assistant that provides structured responses.",
            output_type=output_type,
            model_settings=settings
        )
        
        result = await agent.run(prompt)
        return result.output


def create_client(model_name: str = "x-ai/grok-3-mini") -> XAIClient:
    """xAI 클라이언트 생성 헬퍼 함수"""
    return XAIClient(model_name)