from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langgraph import StateGraph, END
from langchain_core.messages import BaseMessage
from pydantic import BaseModel


class AgentState(BaseModel):
    messages: List[BaseMessage] = []
    context: Dict[str, Any] = {}
    current_step: str = "start"
    completed: bool = False


class BaseAgent(ABC):
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.graph = None
        self.tools = []

    @abstractmethod
    def define_tools(self) -> List:
        """Her agent kendi tool'larını tanımlar"""
        pass

    @abstractmethod
    def build_graph(self) -> StateGraph:
        """Her agent kendi graph yapısını oluşturur"""
        pass

    def initialize(self):
        """Agent'ı başlatır"""
        self.tools = self.define_tools()
        self.graph = self.build_graph()

    async def run(self, initial_state: AgentState) -> AgentState:
        """Agent'ı çalıştırır"""
        if not self.graph:
            self.initialize()

        result = await self.graph.ainvoke(initial_state)
        return result
