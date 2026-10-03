from crewai import Agent
from agents import get_groq_llm
from tools import create_pdf_report

def create_reporter_agent() -> Agent:
    return Agent(
        role="Chief Business Intelligence Officer & Executive Communicator",
        goal="Synthesize raw statistical findings into executive briefs, strategic insights, and PDF exports.",
        backstory="""You are a former McKinsey principal consultant who excels at translating complex quantitative outputs 
        into clear, actionable executive insights. You take structured outputs from data scientists and write crisp, 
        non-technical summaries focused on business value, risks, and recommended action steps.""",
        tools=[create_pdf_report],
        llm=get_groq_llm(),
        verbose=True,
        allow_delegation=False
    )
