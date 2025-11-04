from google.adk.agents import SequentialAgent
from .subagents import summarizer_agent, parallel_agent


root_agent = SequentialAgent(
    name="StockAdvisorWorkflow",
    description="Orchestrates stock price, company news, acquisition research, competitor analysis, and then summarizes the information.",
    sub_agents=[parallel_agent, summarizer_agent],
)