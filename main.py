import os
import asyncio
from dotenv import load_dotenv
import openai

from agents import Agent, Runner, function_tool, SQLiteSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_ID = os.getenv("MODEL_ID", "gpt-3.5-turbo")

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in .env")

# Configure OpenAI client
openai.api_key = OPENAI_API_KEY

print(f"✅ Using model: {MODEL_ID}")

# Persistent session (memory)
session = SQLiteSession("ucm_user", "memory.db")

# Global MCP client reference
mcp_client = None

# Interactive REPL (Chat Loop)
async def repl():
    global mcp_client
    print("Type 'exit' to quit.\n")

    # Create server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["ucm_mcp.py"]
    )

    # Connect to MCP server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as client:
            mcp_client = client
            
            # Initialize the session
            await mcp_client.initialize()
            
            # List available tools
            tools_response = await mcp_client.list_tools()
            print(f"✅ Connected to MCP server with {len(tools_response.tools)} tool(s)")
            
            # Debug: Print available tools
            for tool in tools_response.tools:
                print(f"   - {tool.name}: {tool.description}")
            print()
            
            # Create wrapper function using @function_tool decorator
            @function_tool
            async def get_application_deadlines() -> str:
                """Fetch undergraduate application deadlines from the UCM admissions website."""
                print("[DEBUG] Calling MCP tool get_application_deadlines", flush=True)
                result = await mcp_client.call_tool("get_application_deadlines", arguments={})
                if result.content:
                    content = result.content[0]
                    text_result = content.text if hasattr(content, 'text') else str(content)
                    print(f"[DEBUG] Tool returned: {text_result[:100]}...", flush=True)
                    return text_result
                return "No data returned"

            # Create agent with the decorated function
            agent = Agent(
                name="UCM Admissions Chatbot",
                instructions=(
                    "You are an AI admissions assistant for the University of Central Missouri (UCM).\n"
                    "Use the get_application_deadlines tool to retrieve admissions information from the UCM website.\n"
                    "Always try to call this tool first for any admissions-related questions.\n"
                    "If the tool doesn't have specific information, suggest visiting the official UCM website."
                ),
                tools=[get_application_deadlines],
                model=MODEL_ID,
            )

            while True:
                user_input = input("Ask: ").strip()

                if user_input.lower() in {"exit", "quit"}:
                    break

                try:
                    result = await Runner.run(
                        agent,
                        user_input,
                        session=session
                    )
                    print("\n" + result.final_output + "\n")
                except Exception as e:
                    print(f"⚠️ Error: {e}\n")

def main():
    asyncio.run(repl())

if __name__ == "__main__":
    main()