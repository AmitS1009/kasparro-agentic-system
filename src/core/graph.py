from langgraph.graph import StateGraph, START, END
from src.core.state import AgentState
from src.agents.parser import node_parse_data
from src.agents.strategist import node_strategize_content
from src.agents.writer import node_write_content

def create_graph():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("parser", node_parse_data)
    workflow.add_node("strategist", node_strategize_content)
    workflow.add_node("writer", node_write_content)

    # Add Edges (Linear Flow)
    workflow.add_edge(START, "parser")
    workflow.add_edge("parser", "strategist")
    workflow.add_edge("strategist", "writer")
    workflow.add_edge("writer", END)

    # Compile
    return workflow.compile()
