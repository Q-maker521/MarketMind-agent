from langgraph.graph import END, START, StateGraph

from app.agent.nodes import (
    backtest_runner,
    data_planner,
    indicator_calculator,
    market_data_fetcher,
    news_researcher,
    report_reviewer,
    report_writer,
    task_parser,
)
from app.agent.state import ResearchState


def build_research_workflow():
    graph = StateGraph(ResearchState)

    graph.add_node("task_parser", task_parser)
    graph.add_node("data_planner", data_planner)
    graph.add_node("market_data_fetcher", market_data_fetcher)
    graph.add_node("indicator_calculator", indicator_calculator)
    graph.add_node("news_researcher", news_researcher)
    graph.add_node("backtest_runner", backtest_runner)
    graph.add_node("report_writer", report_writer)
    graph.add_node("report_reviewer", report_reviewer)

    graph.add_edge(START, "task_parser")
    graph.add_edge("task_parser", "data_planner")
    graph.add_edge("data_planner", "market_data_fetcher")
    graph.add_edge("market_data_fetcher", "indicator_calculator")
    graph.add_edge("indicator_calculator", "news_researcher")
    graph.add_edge("news_researcher", "backtest_runner")
    graph.add_edge("backtest_runner", "report_writer")
    graph.add_edge("report_writer", "report_reviewer")
    graph.add_edge("report_reviewer", END)

    return graph.compile()


def run_research_workflow(task: dict) -> ResearchState:
    workflow = build_research_workflow()
    initial_state: ResearchState = {
        "task": task,
        "steps": [],
        "tool_calls": [],
        "errors": [],
    }
    return workflow.invoke(initial_state)
