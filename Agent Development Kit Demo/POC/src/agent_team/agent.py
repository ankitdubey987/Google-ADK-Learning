import asyncio
import warnings

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.genai import types  # For creating message Content/Parts

from core_utils.util import get_logger

from agent_team.tools_util import basic_tools

warnings.filterwarnings("ignore")

logger = get_logger(__name__)

QWEN_8B = "openai/qwen3:8b"
DEFAULT_MODEL = "openai/qwen3:8b"


def get_model(model_name: str) -> LiteLlm:
    return LiteLlm(model_name)


greeting_agent, farewell_agent, weather_agent = None, None, None
root_agent, root_runner = None, None

try:
    weather_agent = Agent(
        name="weather_agent_v1",
        model=get_model(QWEN_8B),
        description="Provides weather information for specific cities.",
        instruction="You are a helpful weather assistant. When the user asks for the weather in a specific city, use the `get_weather` tool to find the information. If the tool returns an error, inform the user politely. If the tool is successful, present the weather report clearly.",
        tools=[basic_tools.get_weather],
    )
    logger.info(
        "Agent created: %s using model: %s", weather_agent.name, weather_agent.model
    )
except Exception as e:
    logger.error("Failed to create weather agent: %s", e)

try:
    greeting_agent = Agent(
        name="greeting_agent_v1",
        model=get_model(QWEN_8B),
        description="Handles simple greetings and hellos using the `say_hello` tool.",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. Use the `say_hello` tool to generate the greeting. If the user provides their name, make sure to pass it to the tool. Do not engage in any other conversation or tasks.",
        tools=[basic_tools.say_hello],
    )
    logger.info(
        "Agent created: %s using model: %s", greeting_agent.name, greeting_agent.model
    )
except Exception as e:
    logger.error("Failed to create greeting agent: %s", e)

try:
    farewell_agent = Agent(
        name="farewell_agent_v1",
        model=get_model(QWEN_8B),
        description="Handles simple goodbyes and farewells using the `say_goodbye` tool.",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a friendly farewell to the user. Use the `say_goodbye` tool to generate the farewell. Do not engage in any other conversation or tasks.",
        tools=[basic_tools.say_goodbye],
    )
    logger.info(
        "Agent created: %s using model: %s", farewell_agent.name, farewell_agent.model
    )
except Exception as e:
    logger.error("Failed to create farewell agent: %s", e)

if greeting_agent and farewell_agent:
    # Let's use a capable model for the root agent to handle orchestration
    root_agent_model = DEFAULT_MODEL

    weather_agent_team = Agent(
        name="weather_agent_v2",
        model=get_model(root_agent_model),
        description="The main coordinator agent. Handles weather requests and delegates greetings/farewells to specialists.",
        instruction="Use the `get_weather` tool ONLY for specific weather requests (e.g., `weather in London`). You have specialized sub-agents: 1. `greeting_agent`: Handles simple greetings like `Hi`, `Hello`. Delegate to it for these. 2. `farewell_agent`: Handles simple farewells like `Bye`, `Goodbye`. Delegate to it for these. Analyze the user's query. If it's a greeting, delegate to `greeting_agent`. If it is a farewell, delegate to `farewell_agent`. If it is a weather request, handle it yourself using `get_weather`. For anything else, respond appropriately or state you cannot handle it.",
        tools=[basic_tools.get_weather],
        sub_agents=[greeting_agent, farewell_agent],
    )
    logger.info(
        "Agent created: %s using model: %s with sub-agents: %s",
        weather_agent_team.name,
        weather_agent_team.model,
        [s_agent.name for s_agent in weather_agent_team.sub_agents],
    )
else:
    logger.error(
        "Cannot create root agent because one or more sub agents failed to initialize or `get_weather` tool is not missing."
    )
    if not greeting_agent:
        logger.error(" - Greeting Agent is missing")
    if not farewell_agent:
        logger.error(" - Farewell Agent is missing")
    if not "get_weather" in globals():
        logger.error(" - `get_weather` tool is missing")


async def call_agent_async(query: str, runner: Runner, user_id: str, session_id: str):
    """
    Calls the agent asynchronously and returns the final response.
    """
    logger.info(">>> User query: %s", query)

    # Create the message
    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."

    # Key concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        logger.info(
            "[Event] Author: %s, Type: %s, Final: %s, Content: %s",
            event.author,
            type(event).__name__,
            event.is_final_response(),
            event.content,
        )

        # Key Concept: is_final_response() marks the concluding message for the turn.
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


async def run_conversation():
    """
    Runs a conversation with the agent.
    """
    # Setup runner and session service
    session_svc = InMemorySessionService()

    APP_NAME = "weather_tutorial_app"
    USER_ID = "user_123"
    SESSION_ID = "session_123"

    # Create the specific session where the conversations will happen
    session = await session_svc.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    logger.info(
        "Session created: App=%s, User=%s, Session=%s", APP_NAME, USER_ID, SESSION_ID
    )

    # Runner
    runner = Runner(agent=weather_agent, session_service=session_svc, app_name=APP_NAME)
    logger.info(
        "Runner created: App=%s, User=%s, Session=%s", APP_NAME, USER_ID, SESSION_ID
    )
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break
        await call_agent_async(user_input, runner, USER_ID, SESSION_ID)


root_agent_var_name = "root_agent"
if "weather_agent_team" in globals():
    root_agent_var_name = "weather_agent_team"
else:
    logger.error(
        "Root Agent ('root_agent' or 'weather_agent_team') not found. Cannot define run_team_conversation."
    )
    root_agent = None  # Or set a flag to prevent execution

if root_agent_var_name in globals() and globals()[root_agent_var_name]:
    # Define the main async function for the conversation logic.
    # The 'await' keywords INSIDE this function are necessary for async operations.
    async def run_team_conversation():
        """
        Runs a conversation with the agent team.
        """
        logger.info("-- Testing Agent Team Delegation --")
        # Setup runner and session service
        session_svc = InMemorySessionService()

        APP_NAME = "weather_tutorial_agent_team"
        USER_ID = "user_1_agent_team"
        SESSION_ID = "session_1_agent_team"

        # Create the specific session where the conversations will happen
        session = await session_svc.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        logger.info(
            "Session created: App=%s, User=%s, Session=%s",
            APP_NAME,
            USER_ID,
            SESSION_ID,
        )

        actual_root_agent = globals()[root_agent_var_name]
        logger.info("Root Agent: %s", actual_root_agent)
        # Runner
        runner = Runner(
            agent=actual_root_agent, session_service=session_svc, app_name=APP_NAME
        )
        logger.info(
            "Runner created: App=%s, User=%s, Session=%s", APP_NAME, USER_ID, SESSION_ID
        )
        while True:
            user_input = input("User: ")
            if user_input.lower() == "exit":
                break
            await call_agent_async(user_input, runner, USER_ID, SESSION_ID)
        logger.info("-- Agent Team Delegation Test Completed --")


def main():
    asyncio.run(run_team_conversation())


if __name__ == "__main__":
    # asyncio.run(run_conversation())
    main()
