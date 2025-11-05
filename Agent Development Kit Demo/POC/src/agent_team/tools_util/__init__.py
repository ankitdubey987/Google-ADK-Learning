from datetime import datetime
from typing import Optional

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from core_utils.util import get_logger

logger = get_logger(__name__)

duck_duck_go_api_wrapper = DuckDuckGoSearchAPIWrapper(source="text", backend="bing")

duck_duck_go_search = DuckDuckGoSearchResults(
    output_format="list", api_wrapper=duck_duck_go_api_wrapper
)


def get_weather(city: str) -> dict:
    """
    Retrieves the weather for a given city.

    Args:
        city (str): The name of the city.

    Returns:
        dict: A dictionary containing the weather information.
            Includes a 'status' key ('success' or 'error').
            If 'success', includes a 'report' key with weather details.
            If 'error', includes an 'error_message' key.
    """
    logger.info("--- Tool: get_weather called for city: %s ---", city)
    city_normalized = city.lower().strip().title()

    resp = duck_duck_go_search.run(
        tool_input={
            "query": f"{city_normalized} weather on {datetime.now().strftime('%Y-%m-%d')}"
        }
    )
    logger.debug("Response: %s", resp)
    if resp:
        return {
            "status": "success",
            "report": ", ".join([item.get("snippet", "") for item in resp]),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Failed to retrieve weather information for {city_normalized}.",
        }


def say_hello(name: Optional[str] = None) -> str:
    """
    Provides a simple greeting. If a name is provided, it will be used.

    Args:
        name (Optional[str]): The name to greet. Defaults to None.

    Returns:
        str: A friendly greeting message.
    """
    if name:
        greeting = f"Hello, {name}!"
        logger.info("--- Tool: say_hello called for name: %s ---", name)
    else:
        greeting = "Hello There!"
        logger.info("--- Tool: say_hello called without name ---")

    return greeting


def say_goodbye() -> str:
    """
    Provides a simple farewell message to conclude the conversation.
    """
    logger.info("--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day!"


if __name__ == "__main__":
    from pprint import pprint

    input_city = input("Enter city: ")
    pprint(get_weather(input_city))

    print(say_hello("John"))
    print(say_goodbye())
