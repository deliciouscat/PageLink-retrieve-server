"""
JSON 파싱 모듈
pydantic-ai와 기존 문자열 기반 JSON 파싱을 모두 지원
"""
import json
import re
from typing import TypeVar, Type, Any, Union
from pydantic import BaseModel, ValidationError

T = TypeVar('T', bound=BaseModel)

def json_parser(json_string: str) -> dict:
    """
    기존 문자열 기반 JSON 파싱 함수
    markdown 코드 블록에서 JSON을 추출하고 파싱
    
    Args:
        json_string: JSON 문자열 (markdown 코드 블록 포함 가능)
        
    Returns:
        dict: 파싱된 JSON 객체
        
    Raises:
        json.JSONDecodeError: JSON 파싱 실패시
    """
    # markdown 코드 블록 제거
    cleaned_json = json_string.replace("```json", "").replace("```", "").strip()
    
    # 추가적인 정리: 앞뒤 공백 및 불필요한 문자 제거
    cleaned_json = re.sub(r'^[^{[]*', '', cleaned_json)  # JSON 시작 전 불필요한 문자 제거
    cleaned_json = re.sub(r'[^}\]]*$', '', cleaned_json)  # JSON 끝 후 불필요한 문자 제거
    
    return json.loads(cleaned_json)

def structured_parser(json_string: str, output_type: Type[T]) -> T:
    """
    pydantic 모델을 사용한 구조화된 JSON 파싱 함수
    
    Args:
        json_string: JSON 문자열
        output_type: 파싱할 pydantic 모델 타입
        
    Returns:
        T: 파싱된 pydantic 모델 인스턴스
        
    Raises:
        ValidationError: 유효성 검사 실패시
        json.JSONDecodeError: JSON 파싱 실패시
    """
    # 먼저 기본 JSON 파싱
    parsed_dict = json_parser(json_string)
    
    # pydantic 모델로 검증 및 변환
    return output_type.model_validate(parsed_dict)

def safe_json_parser(json_string: str, output_type: Type[T] = None) -> Union[dict, T, None]:
    """
    안전한 JSON 파싱 함수 - 예외를 잡아서 None 반환
    
    Args:
        json_string: JSON 문자열
        output_type: 선택적 pydantic 모델 타입
        
    Returns:
        Union[dict, T, None]: 파싱 성공시 결과, 실패시 None
    """
    try:
        if output_type:
            return structured_parser(json_string, output_type)
        else:
            return json_parser(json_string)
    except (json.JSONDecodeError, ValidationError, Exception) as e:
        print(f"⚠️ [JSON Parser] 파싱 실패: {e}")
        return None

# 하위 호환성을 위한 별칭
str_to_json = json_parser 