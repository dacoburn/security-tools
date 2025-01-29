import os
from core.plugins.sumologic import Sumologic


def load_sumo_logic_plugin():
    """
    Loads the Sumologic plugin if it is enabled and properly configured.

    :return: Instance of the Sumologic class or None if not enabled/configured.
    """
    sumo_logic_enabled = os.getenv("SUMO_LOGIC_ENABLED", "false").lower() == "true"
    if not sumo_logic_enabled:
        print("Sumo Logic integration is disabled.")
        return None

    sumo_logic_http_source_url = os.getenv("INPUT_SUMO_LOGIC_HTTP_SOURCE_URL")

    if not all([sumo_logic_http_source_url]):
        print("Sumo Logic environment variables are not properly configured!")
        return None

    return Sumologic(sumo_logic_http_source_url)
