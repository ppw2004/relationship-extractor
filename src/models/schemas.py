"""数据模型定义"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Entity(BaseModel):
    """实体模型"""
    name: str = Field(..., description="实体名称")
    type: str = Field(..., description="实体类型，如 Person, Organization, Location 等")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="实体其他属性")


class Relation(BaseModel):
    """关系模型"""
    from_entity: str = Field(..., alias="from", description="起始实体名称")
    to_entity: str = Field(..., alias="to", description="目标实体名称")
    type: str = Field(..., description="关系类型")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="关系其他属性")

    class Config:
        populate_by_name = True


class ExtractionResult(BaseModel):
    """提取结果模型"""
    entities: List[Entity] = Field(default_factory=list, description="提取的实体列表")
    relations: List[Relation] = Field(default_factory=list, description="提取的关系列表")
    raw_text: Optional[str] = Field(None, description="原始文本")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "entities": [e.model_dump() for e in self.entities],
            "relations": [r.model_dump(by_alias=True) for r in self.relations],
            "raw_text": self.raw_text
        }


class LLMResponse(BaseModel):
    """LLM 响应模型"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    reasoning_content: Optional[str] = Field(None, description="深度思考内容")
    success: bool = True
    error: Optional[str] = None
