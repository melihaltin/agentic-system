from typing import Dict, Any, List
from abc import ABC, abstractmethod
from langgraph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel
import asyncio


class AgentState(BaseModel):
    messages: List[BaseMessage] = []
    context: Dict[str, Any] = {}
    phone_number: str = ""
    session_id: str = ""
    completed: bool = False


class BaseAgent(ABC):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.graph = None
        self.tools = []

    @abstractmethod
    def define_tools(self):
        """Agent'ın kullanacağı tool'ları tanımlar"""
        pass

    @abstractmethod
    def build_workflow(self) -> StateGraph:
        """Agent'ın workflow'unu oluşturur"""
        pass

    def initialize(self):
        """Agent'ı başlatır"""
        self.tools = self.define_tools()
        self.graph = self.build_workflow()

    async def process_call(
        self, phone_number: str, user_input: str = ""
    ) -> Dict[str, Any]:
        """Telefon aramasını işler"""
        if not self.graph:
            self.initialize()

        initial_state = AgentState(
            messages=[HumanMessage(content=user_input)] if user_input else [],
            phone_number=phone_number,
            session_id=phone_number.replace("+", "").replace("-", ""),
            context={"step": "greeting"},
        )

        result = await self.graph.ainvoke(initial_state)
        return result
