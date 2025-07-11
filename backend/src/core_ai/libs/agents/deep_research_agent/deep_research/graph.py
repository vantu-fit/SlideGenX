from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState, ResearchState
from .struct import SectionOutput
from .nodes import (
    report_structure_planner_node,
    human_feedback_node,
    section_formatter_node,
    parallel_research_agent_node,
    finalizer_node
)

# <<< ----- RESEARCH AGENT ----- >>>


# <<< ----- MAIN AGENT ----- >>>

memory_saver = MemorySaver()

builder = StateGraph(AgentState)

builder.add_node("report_structure_planner", report_structure_planner_node)
builder.add_node("human_feedback", human_feedback_node)
builder.add_node("section_formatter", section_formatter_node)
builder.add_node("parallel_research_agent", parallel_research_agent_node)
builder.add_node("finalizer", finalizer_node)

builder.set_entry_point("report_structure_planner")
builder.add_edge("report_structure_planner", "human_feedback")
builder.add_edge("human_feedback", "section_formatter")
builder.add_edge("section_formatter", "parallel_research_agent")  
builder.add_edge("parallel_research_agent", "finalizer")         
builder.add_edge("finalizer", END)

agent_graph = builder.compile(checkpointer=memory_saver)