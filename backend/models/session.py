from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Session(BaseModel):
    session_id: str
    mode: str = "auto"
    selected_item_id: Optional[str] = None
    buyer_agent: Optional[Dict[str, Any]] = None
    evaluator_agents: List[Dict[str, Any]] = Field(default_factory=list)
    seller_agents: List[Dict[str, Any]] = Field(default_factory=list)
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    turn: int = 0
