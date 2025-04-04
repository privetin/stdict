import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path

import mcp.types as types
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("stdict")

SEARCH_API_URL = "https://stdict.korean.go.kr/api/search.do"


def get_api_key():
    # First try environment variable
    api_key = os.environ.get("STDICT_API_KEY")
    if api_key:
        return api_key

    # Then try Claude desktop config
    config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
                if "mcpServers" in config and "stdict" in config["mcpServers"]:
                    env = config["mcpServers"]["stdict"].get("env", {})
                    if "STDICT_API_KEY" in env:
                        return env["STDICT_API_KEY"]
        except:
            pass

    raise ValueError(
        "API key not found. Please set the STDICT_API_KEY environment variable or configure it in Claude desktop config."
    )


API_KEY = get_api_key()


@mcp.tool()
def search(
    query: str,
    api_key: str = API_KEY,
    req_type: str = "json",
    start: int = 1,
    num: int = 10,
    advanced: bool = False,
    target: int = 1,
    method: str = "exact",
    type1: str = "all",
    type2: str = "all",
    pos: str = "0",
    cat: str = "0",
    multimedia: str = "0",
    letter_s: int = 1,
    letter_e: int = 1,
    update_s: str = None,
    update_e: str = None
) -> list[types.TextContent | types.ImageContent]:
    """
    Search the Korean Standard Dictionary

    Args:
        query: Search term in Korean
        api_key: Your Standard Korean Dictionary API key
        start: Starting position (default: 1)
        num: Number of results to return (default: 10)
        advanced: Whether to use advanced search (default: False)
        req_type: Response format type, either "json" or "xml" (default: "json")
        target: Search target (default: 1 - 표제어)
        method: Search method (default: "exact")
        type1: Type 1 filter (default: "all")
        type2: Type 2 filter (default: "all")
        pos: Part of speech filter (default: "0" - 전체)
        cat: Category filter (default: "0" - 전체)
        multimedia: Multimedia filter (default: "0" - 전체)
        letter_s: Starting syllable count (default: 1)
        letter_e: Ending syllable count (default: 1)
        update_s: Start date for updates (optional)
        update_e: End date for updates (optional)

    Returns:
        Search results from the Korean Standard Dictionary in its original format
    """
    params = {
        "key": api_key,
        "q": query,
        "req_type": req_type,
        "start": start,
        "num": num,
        "advanced": "y" if advanced else "n",
    }

    if advanced:
        advanced_params = {
            "target": target,
            "method": method,
            "type1": type1,
            "type2": type2,
            "pos": pos,
            "cat": cat,
            "multimedia": multimedia,
            "letter_s": letter_s,
            "letter_e": letter_e,
        }
        
        # Only add date parameters if they're provided
        if update_s:
            advanced_params["update_s"] = update_s
        if update_e:
            advanced_params["update_e"] = update_e
            
        params.update(advanced_params)

    try:
        response = requests.get(SEARCH_API_URL, params=params)
        response.raise_for_status()
        
        # Return the original XML response as text
        return [types.TextContent(type="text", text=response.text)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
