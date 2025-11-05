import asyncio
import datetime
from zoneinfo import ZoneInfo

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from langchain_community.tools import DuckDuckGoSearchResults

from core_utils.util import get_logger

logger = get_logger(__name__)

USER_ID = "user_123"
SESSION_ID = "session_123"
APP_NAME = "weather_time_tool_agent"

DEFAULT_MODEL = "openai/mistral:7b"


def get_weather(city: str) -> dict:
    """
    Retrieves the current city weather report for a specified city.

    Args:
        city (str): The city to retrieve the weather report for.

    Returns:
        dict: status and result or error message
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": "The weather in New York is sunny with a temperature of 25 degrees Celsius (77 degrees Fahrenheit)",
        }
    else:
        duck_duck_go_search_tool = DuckDuckGoSearchResults(
            num_results=2, output_format="json"
        )
        resp = duck_duck_go_search_tool.run(
            tool_input={
                "query": f"{city} weather on {datetime.datetime.now().strftime('%Y-%m-%d')}"
            }
        )
        return {"status": "success", "report": f"The weather in {city} is {resp}"}


def get_current_time(city: str) -> dict:
    """
    Retrieves the current time for a specified city.

    Args:
        city (str): The city to retrieve the current time for.

    Returns:
        dict: status and result or error message
    """
    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have time information for {city}",
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return {
        "status": "success",
        "result": f"The current time in {city} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}",
    }


root_agent = Agent(
    name="weather_time_agent",
    model=LiteLlm(DEFAULT_MODEL),
    description="Agent to answer questions about time and weather in a city",
    instruction="You are a helpful agent who can answer user questions about the time and weather in a city.",
    tools=[get_weather, get_current_time],
)


async def run_stock_advisor_workflow():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    runner = Runner(
        agent=root_agent, session_service=session_service, app_name=APP_NAME
    )

    user_query = input("User: ")
    final_response_text = "Agent did not produce a final response."
    logger.info(">>> User query: %s", user_query)
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=types.Content(role="user", parts=[types.Part(text=user_query)]),
    ):
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
