from datetime import datetime
from typing import Any, Dict, Optional

from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import BaseTool, ToolContext
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools import DuckDuckGoSearchResults
from core_utils.util import get_logger

logger = get_logger(__name__)

MODEL = "ollama_chat/qwen3:8b"

duck_duck_go_search = LangchainTool(
    DuckDuckGoSearchResults(num_results=5, output_format="json")
)


def add_todays_date_to_search_tool(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
    agent_name = tool_context.agent_name
    tool_name = tool.name
    logger.info("[Callback] Agent: %s, Tool: %s", agent_name, tool_name)
    logger.info("[Callback] Args: %s", args)
    logger.info("[Callback] Tool Context: %s", tool_context)

    if tool_name == "duckduckgo_results_json":
        logger.info("[Callback] Tool Name: %s Modifying args.", tool_name)
        args["query"] = (
            f"{args['query']} Todays date: {datetime.now().strftime('%Y-%m-%d')}"
        )
        logger.info("[Callback] Modified Args: %s", args)
        return None

    logger.info("[Callback] Tool Name: %s Not modifying args.", tool_name)
    return None


# Acquisition Research Agent: Specialized in researching acquisitions and mergers.
acquisition_research_agent = LlmAgent(
    model=LiteLlm(model=MODEL),
    description="You are a acquisition finder agent",
    instruction="""
    Acts as a acquisition finder agent. You can access the following tool to get information about acquisitions and mergers.

    Tools Available:
    - duck_duck_go_search

    Output Instructions:
    - If the user does not provide specific details, make reasonable assumptions about the company and search for information about acquisitions and mergers.
    - If the user provides specific details, search for information about acquisitions and mergers based on the user's input.
    - If the user provides invalid details, return a valid JSON with all the relevant information about acquisitions and mergers and news.
    - You return a valid JSON with all the relevant information about acquisitions and mergers and news.
    """,
    name="AcquisitionResearchAgent",
    tools=[duck_duck_go_search],
    before_tool_callback=add_todays_date_to_search_tool,
    output_key="acquisition_research",
)

# Stock Price Agent: Specialized in retrieving stock prices.
stock_price_agent = LlmAgent(
    model=LiteLlm(model=MODEL),
    description="You are a stock price agent",
    instruction="""
    Acts as a stock price agent. You can access the following tools to get information about stock prices.

    Tools Available:
    - duck_duck_go_search

    Output Instructions:
    - If the user does not provide specific details, make reasonable assumptions about the company and search for information about stock prices.
    - If the user provides specific details, search for information about stock prices based on the user's input.
    - If the user provides invalid details, return a valid JSON with all the relevant information about stock prices and news.
    - You return a valid JSON with all the relevant information about stock prices and news.
    """,
    name="StockPriceAgent",
    tools=[duck_duck_go_search],
    output_key="stock_price",
)

# Company News Retriever Agent: Specialized in retrieving company news.
company_news_retriever_agent = LlmAgent(
    model=LiteLlm(model=MODEL),
    description="You are a company news retriever agent",
    instruction="""
    Acts as a company news retriever agent. You can access the following tools to get information about company news.

    Tools Available:
    - duck_duck_go_search

    Output Instructions:
    - If the user does not provide specific details, make reasonable assumptions about the company and search for information about company news.
    - If the user provides specific details, search for information about company news based on the user's input.
    - If the user provides invalid details, return a valid JSON with all the relevant information about company news and news.
    - You return a valid JSON with all the relevant information about company news and news.
    """,
    name="CompanyNewsRetrieverAgent",
    tools=[duck_duck_go_search],
    output_key="company_news",
)

# Competitor Analysis Agent: Specialized in analyzing competitors.
competitor_analysis_agent = LlmAgent(
    model=LiteLlm(model=MODEL),
    description="You are a competitor analysis agent",
    instruction="""
    Acts as a competitor analysis agent. You can access the following tools to get information about competitors.

    Tools Available:
    - duck_duck_go_search

    Output Instructions:
    - If the user does not provide specific details, make reasonable assumptions about the company and search for information about competitors.
    - If the user provides specific details, search for information about competitors based on the user's input.
    - If the user provides invalid details, return a valid JSON with all the relevant information about competitors and news.
    - You return a valid JSON with all the relevant information about competitors and news.
    """,
    name="CompetitorAnalysisAgent",
    tools=[duck_duck_go_search],
    output_key="competitor_analysis",
)

parallel_agent = ParallelAgent(
    name="ParallelAgent",
    description="You are a parallel agent",
    sub_agents=[stock_price_agent, competitor_analysis_agent],
)

summarizer_agent = LlmAgent(
    model=LiteLlm(model=MODEL),
    description="You are a summarizer agent",
    instruction="""
    Summarize JSON responses into a single summary document with all the information provided by the other agents into a detailed report in the markdown format. Make sure to include all the relevant information from the other agents.
    1. Stock Price Agent: {{stock_price}}
    2. Competitor Analysis Agent: {{competitor_analysis}}

    - Ensure the summary is well-structured and clearly presents all trip details in an organized manner.
    """,
    name="SummarizerAgent",
    output_key="summarizer",
)
