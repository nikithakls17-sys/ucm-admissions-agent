import os
import asyncio
from dotenv import load_dotenv
import openai
from agents import Agent, Runner, function_tool, SQLiteSession

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_ID = os.getenv("MODEL_ID", "gpt-3.5-turbo")

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in .env")

# Configure OpenAI client (official endpoint)
openai.api_key = OPENAI_API_KEY
openai.api_base = "https://api.openai.com/v1"

print(f"✅ Using model: {MODEL_ID}")

# -------------------------------
# Persistent session (memory)
# -------------------------------
session = SQLiteSession("ucm_user", "memory.db")

# -------------------------------
# Define Tools for UCM Admissions
# -------------------------------
@function_tool
def get_undergraduate_requirements() -> str:
    """
    Returns general undergraduate admission requirements.
    """
    return (
        "Undergraduate Admission Requirements:\n"
        "- Completed online application form.\n"
        "- Official high school transcript or GED.\n"
        "- ACT/SAT scores (optional for most programs).\n"
        "- Minimum 2.0 GPA for standard admission.\n"
        "- International students must provide proof of English proficiency (TOEFL, IELTS, Duolingo).\n"
        "Visit: https://www.ucmo.edu/future-students/admissions/"
    )

@function_tool
def get_application_deadlines() -> str:
    """
    Returns application deadlines for major terms.
    """
    return (
        "Application Deadlines:\n"
        "- Fall Semester: May 1\n"
        "- Spring Semester: November 1\n"
        "- Summer Semester: March 1\n"
        "It’s recommended to apply early for scholarships and housing.\n"
        "Source: https://www.ucmo.edu/future-students/admissions/"
    )

@function_tool
def get_contact_info() -> str:
    """
    Returns contact details for UCM Admissions Office.
    """
    return (
        "UCM Admissions Contact:\n"
        "📍 Office: Ward Edwards 1400, Warrensburg, MO 64093\n"
        "📞 Phone: 660-543-4290\n"
        "✉️ Email: admit@ucmo.edu\n"
        "🌐 Website: https://www.ucmo.edu/future-students/admissions/"
    )

@function_tool
def get_scholarship_info() -> str:
    """
    Provides scholarship information overview.
    """
    return (
        "Scholarship Information:\n"
        "- UCM offers automatic scholarships based on GPA and test scores.\n"
        "- International students are eligible for merit-based scholarships.\n"
        "- Some departmental and competitive awards require separate applications.\n"
        "Learn more: https://www.ucmo.edu/future-students/financial-aid/"
    )

@function_tool
def get_housing_info() -> str:
    """
    Provides details about UCM student housing.
    """
    return (
        "Housing and Residence Life:\n"
        "- UCM offers traditional, suite-style, and apartment-style housing.\n"
        "- First-year students typically stay in residence halls.\n"
        "- Applications for housing open once you’re admitted.\n"
        "Visit: https://www.ucmo.edu/future-students/housing/"
    )

# -------------------------------
# Define the AI Agent
# -------------------------------
agent = Agent(
    name="UCM Admissions Chatbot",
    instructions=(
        "You are an AI admissions assistant for the University of Central Missouri (UCM).\n"
        "Your goal is to help prospective students with accurate admission information.\n"
        "Use the provided tools to answer questions. If unsure, direct the user to the official UCM Admissions website.\n"
        "Keep answers clear, friendly, and factual."
    ),
    tools=[
        get_undergraduate_requirements,
        get_application_deadlines,
        get_contact_info,
        get_scholarship_info,
        get_housing_info,
    ],
    model=MODEL_ID,
)

# -------------------------------
# Interactive REPL (Chat Loop)
# -------------------------------
async def repl():
    print("Type 'exit' to quit.")
    while True:
        user_input = input("Ask: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break

        try:
            result = await Runner.run(agent, user_input, session=session)
            print("\n" + result.final_output + "\n")
        except Exception as e:
            print(f"⚠️ Error: {e}\n")

def main():
    asyncio.run(repl())

if __name__ == "__main__":
    main()
