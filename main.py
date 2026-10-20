"""
xiaoA-RAG - Main Entry Point

Delegates to the MCP stdio server. Configuration is validated lazily when
tools are invoked, so the server can start and respond to `list_tools`
even before a provider API key is configured.
"""

import sys

from src.mcp_server.server import run_stdio_server


def main() -> int:
    """
    Main entry point for the MCP Server.

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    return run_stdio_server()


if __name__ == "__main__":
    sys.exit(main())
