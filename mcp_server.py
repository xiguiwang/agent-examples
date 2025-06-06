import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# 创建 MCP Server
mcp = FastMCP("pyfile_count")

@mcp.tool()
async def count_desktop_python_files() -> int:
    """Count the number of .py files in my desktop ."""
    # Get the desktop path
    username = os.getenv("USER") or os.getenv("USERNAME")
    desktop_path = Path(f"/home/{username}")

    # Count .txt files
    py_files = list(desktop_path.glob("*.py"))
    return len(py_files)

@mcp.tool()
async def list_dir_py_files(in_dir: str) -> str:
    """Get a list of all .py filenames on a directory."""
    # Get the desktop path
    #username = os.getenv("USER") or os.getenv("USERNAME")
    #desktop_path = Path(f"/home/{username}")
    dir_path = Path(f"{in_dir}")

    # Get all .txt files
    py_files = list(dir_path.glob("*.py"))

    # Return the filenames
    if not py_files:
        return "No .py files found on desktop."

    # Format the list of filenames
    file_list = "\n".join([f"- {file.name}" for file in py_files])
    return f"Found {len(py_files)} .py files on desktop:\n{file_list}"

if __name__ == "__main__":
    # Initialize and run the server
    #mcp.run()
    mcp.run(transport="stdio")
