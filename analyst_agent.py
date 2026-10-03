from crewai import Agent
from agents import get_groq_llm
from tools import profile_csv_dataset, generate_plotly_chart_config

def create_analyst_agent() -> Agent:
    return Agent(
        role="Lead Quantitative Data Scientist & EDA Specialist",
        goal="Execute deterministic data profiling, inspect distributions, identify statistical anomalies, and generate chart configs.",
        backstory="""You are a meticulous Senior Data Scientist who relies strictly on calculated statistical metrics. 
        You NEVER guess numbers or invent stats. You always invoke Python tools to profile datasets, assess missingness, 
        and configure Plotly visualizations based on true underlying column distributions.""",
        tools=[profile_csv_dataset, generate_plotly_chart_config],
        llm=get_groq_llm(),
        verbose=True,
        allow_delegation=False
    )
