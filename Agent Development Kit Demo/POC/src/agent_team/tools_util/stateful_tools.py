from google.adk.tools.tool_context import ToolContext

from core_utils.util import get_logger

from agent_team.tools_util import basic_tools

logger = get_logger(__name__)


def to_fahrenheit(temp_in_celsius: int) -> float:
    """
    Converts temperature in Celsius to Fahrenheit
    """
    return (temp_in_celsius * 9 / 5) + 32  # Calculate Fahrenheit


def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """
    Retrieves weather, converts temp unit based on session state.
    """

    logger.info("--- Tool: get_weather_stateful called for %s", city)

    # Read preferred state object
    preferred_unit = tool_context.state.get(
        "user_preference_temperature_unit", "Celsius"
    )  # Default to Celsius
    logger.info(
        "--- Tool: Reading state 'user_preferred_temperature_unit': %s", preferred_unit
    )

    resp = basic_tools.get_weather(city)

    if resp.get("status") == "success":
        from random import randrange

        mock_temp = randrange(0, 100)
        condition = resp["report"]

        if preferred_unit == "Fahrenheit":
            temp_val = to_fahrenheit(mock_temp)
            temp_unit = "F"
        else:
            temp_val = mock_temp
            temp_unit = "C"

        resp["report"] = f"{condition}. Temperature is {temp_val:0.2f}{temp_unit}"

        logger.info(
            "--- Tool: Generated Report in %s. Result: %s ---", preferred_unit, resp
        )

        # Writing back to state (Optional for this tool)
        tool_context.state["last_city_checked_stateful"] = city
        logger.info("--- Tool: Updated state 'last_city_checked_stateful: %s ---", city)

    return resp
