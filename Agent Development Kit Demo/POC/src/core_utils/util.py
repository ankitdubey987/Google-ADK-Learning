import logging
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService


def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(lineno)d - %(message)s",
    )
    return logging.getLogger(name)

def get_model(model_name: str) -> LiteLlm:
    return LiteLlm(model_name)