import asyncio
from google.adk.agents import SequentialAgent
from .subagents import summarizer_agent, parallel_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from core_utils.util import get_logger

logger = get_logger(__name__)

USER_ID = "user_123"
SESSION_ID = "session_123"
APP_NAME = "stock_advisor_workflow"


root_agent = SequentialAgent(
    name="StockAdvisorWorkflow",
    description="Orchestrates stock price, company news, acquisition research, competitor analysis, and then summarizes the information.",
    sub_agents=[parallel_agent, summarizer_agent],
)

async def run_stock_advisor_workflow():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    runner = Runner(agent=root_agent, session_service=session_service, app_name=APP_NAME)

    user_query = input("User: ")
    final_response_text = "Agent did not produce a final response."
    logger.info(">>> User query: %s", user_query)
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=types.Content(role="user", parts=[types.Part(text=user_query)])):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
                logger.info("Final response: %s", final_response_text)
            elif (
                event.actions and event.actions.escalate
            ):  # Handle potential errors/escalations
                final_response_text = f"Agent escalated: {event.error_message or 'No specific error message'}"
                logger.info(final_response_text)
            break
    
    logger.info("<<< Agent response: %s", final_response_text)

def run_stock_advisor_workflow_sync():
    asyncio.run(run_stock_advisor_workflow())