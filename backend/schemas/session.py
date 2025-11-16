from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SessionCreateRequest(BaseModel):
    mode: Optional[str] = "auto"
    selected_item_id: Optional[str] = None
    buyer_agent: Optional[Dict[str, Any]] = None
    evaluator_agents: Optional[List[Dict[str, Any]]] = None
    seller_agents: Optional[List[Dict[str, Any]]] = None
    messages: Optional[List[Dict[str, Any]]] = None
    turn: Optional[int] = 0
