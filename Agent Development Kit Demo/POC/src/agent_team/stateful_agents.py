import asyncio

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agent_team.agent import call_agent_async
from agent_team.tools_util import basic_tools, stateful_tools
from core_utils.util import get_logger, get_model

logger = get_logger(__name__)

QWEN_8B = "openai/qwen3:8b"
_APP_NAME = "stateful_weather_agent_team"
_SESSION_ID_STATEFUL = "session_state_demo_1"
_USER_ID_STATEFUL = "user_state_1"
_SESSION_SVC = InMemorySessionService()

greeting_agent = None
try:
    greeting_agent = Agent(
        model=get_model(QWEN_8B),
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the `say_hello` tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[basic_tools.say_hello],
    )
    logger.info("Agent %s redefined", greeting_agent.name)
except Exception as e:
    logger.exception("Could not redefine Greetings agent. Error %s", e)

farewell_agent = None
try:
    farewell_agent = Agent(
        model=get_model(QWEN_8B),
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[basic_tools.say_goodbye],
    )
    logger.info("Agent %s redefined", farewell_agent.name)
except Exception as e:
    logger.exception("Could not redefine Farewell Agent. Error: %s", e)

# Define Updated Root Agent
root_agent_stateful = None
runner_root_stateful = None

# Check before creating the root agent
if greeting_agent and farewell_agent:
    root_agent_model = QWEN_8B

    root_agent_stateful = Agent(
        name="weather_agent_v4_stateful",
        model=get_model(root_agent_model),
        description="Main agent: Provides weather (state-aware unit), delegates greetings/farewells, saves report to state.",
        instruction="You are the main Weather Agent. Your job is to provide weather using 'get_weather_stateful'. The Tool will format the temperature based on user preference stored in the state. Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. Handle only weather requests, greetings, and farewells.",
        tools=[stateful_tools.get_weather_stateful],
        sub_agents=[greeting_agent, farewell_agent],
        output_key="last_weather_report",
    )

    logger.info(
        "Root Agent: %s created using stateful tool and output_key.",
        root_agent_stateful.name,
    )

    runner_root_stateful = Runner(
        agent=root_agent_stateful, app_name=_APP_NAME, session_service=_SESSION_SVC
    )
    logger.info(
        "Runner created for stateful root agent %s using stateful session service",
        root_agent_stateful.name,
    )
else:
    logger.warning("Cannot create stateful root_agent. Prerequisite missing.")
    if not greeting_agent:
        logger.error("- greeting_agent definition missing")
    if not farewell_agent:
        logger.error("- farewell_agent definition missing")

if "runner_root_stateful" in globals() and runner_root_stateful:

    async def run_team_with_session_state():
        """
        Runs a conversation with the stateful agent teams.
        """
        logger.info(
            "--- New InMemorySessionService stateful agent conversation created for state demonstration ---"
        )

        # Define initial state data - user prefers Celsius initially
        initial_state = {"user_preference_temperature_unit": "Celsius"}

        # Create session, providing the initial state
        session_stateful = await _SESSION_SVC.create_session(
            app_name=_APP_NAME,
            user_id=_USER_ID_STATEFUL,
            session_id=_SESSION_ID_STATEFUL,
            state=initial_state,  # << Initializing state during session creation
        )
        logger.info(
            "Session %s created for user %s.", _SESSION_ID_STATEFUL, _USER_ID_STATEFUL
        )

        user_query = input("Enter your query: ")

        await call_agent_async(
            query=user_query,
            runner=runner_root_stateful,
            user_id=_USER_ID_STATEFUL,
            session_id=_SESSION_ID_STATEFUL,
        )

        logger.info("--- Manually Updating State: Setting unit to Fahrenheit ---")
        try:
            stored_session = _SESSION_SVC.sessions[_APP_NAME][_USER_ID_STATEFUL][
                _SESSION_ID_STATEFUL
            ]
            stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
            logger.info(
                "Stored session state updated. Current 'user_preference_temperature_unit': %s",
                stored_session.state.get("user_preference_temperature_unit", "Not Set"),
            )
        except KeyError as ke:
            logger.error(
                "--- Error: Could not retrieve session %s from internal storage for user %s in app %s to update state. Check IDs and if session was created. --- ",
                _SESSION_ID_STATEFUL,
                _USER_ID_STATEFUL,
                _APP_NAME,
            )
        except Exception as e:
            logger.exception("--- Error updating internal session state: %s ---", e)

        logger.info("Turn 2: Requesting weather in New York (expect Fahrenheit)")
        await call_agent_async(
            query="Tell me the weather in New York",
            runner=runner_root_stateful,
            user_id=_USER_ID_STATEFUL,
            session_id=_SESSION_ID_STATEFUL,
        )

        logger.info("Turn 3: Sending a greeting")
        await call_agent_async(
            query="Hi!",
            user_id=_USER_ID_STATEFUL,
            session_id=_SESSION_ID_STATEFUL,
            runner=runner_root_stateful,
        )

        logger.info("--- Inspecting Final session State ---")
        final_session = await _SESSION_SVC.get_session(
            app_name=_APP_NAME,
            user_id=_USER_ID_STATEFUL,
            session_id=_SESSION_ID_STATEFUL,
        )

        if final_session:
            logger.info(
                "Final Preference: %s",
                final_session.get("user_preference_temperature_unit", "Not Set"),
            )
            logger.info(
                "Final Last Weather Report (from output_key): %s",
                final_session.get("last_weather_report", "Not Set"),
            )
            logger.info(
                "Final Last City Checked (by tool): %s",
                final_session.get("last_city_checked_stateful", "Not Set"),
            )
        else:
            logger.warning("Error: Could not retrieve final session state.")


def main():
    asyncio.run(run_team_with_session_state())


if __name__ == "__main__":
    main()
