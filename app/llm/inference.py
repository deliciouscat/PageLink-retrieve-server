# 필요 기능:
# 1. 모델 별 라우팅
# 2. API 키 관리
import os
from pydantic_ai import Agent
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic import BaseModel
from typing import Type, TypeVar, Any, Optional

'''
이미 완성된 프롬프트를 받아서 인퍼런스

# input
model_name: str
prompt: str

# output

'''

async def inference(prompt: str, model_name: str, model_settings: dict, system_prompt: Optional[str] = None):
    model = OpenAIChatModel(
        model_name,
        provider=OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY")),
    )
    agent_kwargs = {
        "model": model,
        "model_settings": model_settings,
    }
    if system_prompt: agent_kwargs["system_prompt"] = system_prompt
    
    agent = Agent(
        **agent_kwargs,
    )
    result = await agent.run(prompt)
    return result


async def structured_inference(
    prompt: str, 
    model_name: str, 
    model_settings: dict, 
    system_prompt: Optional[str] = None,
    output_type: Optional[Type[BaseModel]] = None
) -> Any:
    """구조화된 출력을 위한 새로운 inference 함수"""
    model = OpenAIChatModel(
        model_name,
        provider=OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY")),
    )
    agent = Agent(
        model,
        model_settings=model_settings,
        system_prompt=system_prompt,
        output_type=output_type  # 구조화된 출력 타입 지정
    )
    result = await agent.run(prompt)
    return result