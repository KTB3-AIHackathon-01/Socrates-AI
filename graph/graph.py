from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict
from operator import add
from dotenv import load_dotenv
import asyncio

load_dotenv()

gpt_model = ChatOpenAI(model_name="gpt-5-nano", temperature=0.7)

class SimpleState(TypedDict):
  user_input: str
  ai_response: str

def ask_gpt(state: SimpleState) -> SimpleState:
  response = gpt_model.invoke(state["user_input"])
  state["ai_response"] = response.content
  return state

async def set_graph(user_input: str) -> str:
  graph = StateGraph(SimpleState)
  graph.add_node("ask_gpt", ask_gpt)

  graph.add_edge(START, "ask_gpt")
  graph.add_edge("ask_gpt", END)

  compiled = graph.compile()
  # 동기 작업을 별도 스레드에서 실행 (블로킹 방지)
  loop = asyncio.get_event_loop()
  result = await loop.run_in_executor(
    None,
    compiled.invoke,
    {"user_input": user_input, "ai_response": ""}
  )
  
  print(result)
  return result['ai_response']