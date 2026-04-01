from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama

# 1. Initialize the Free Local LLM (Ensure Ollama is running)
local_llm = Ollama(model="llama3")

def create_trading_crew(stock_context):
    # Free Technical Analyst Agent
    analyst = Agent(
        role='Senior Technical Analyst',
        goal='Analyze price action and indicators for entry signals',
        backstory="Open-source AI specialist in Nifty50 price action.",
        allow_delegation=False,
        verbose=True,
        llm=local_llm  # <--- Using Local LLM
    )

    # Free Risk Manager Agent
    risk_manager = Agent(
        role='Risk Manager',
        goal='Validate signals against strict stop-loss and capital rules',
        backstory="Conservative risk officer ensuring no trade exceeds 2% capital risk.",
        allow_delegation=True,
        verbose=True,
        llm=local_llm  # <--- Using Local LLM
    )

    # Tasks remain the same but now run on your local machine
    analysis_task = Task(
        description=f"Analyze this data: {stock_context}. Provide a Buy/Sell/Hold recommendation.",
        agent=analyst,
        expected_output="A clear trading signal with technical reasoning."
    )

    risk_task = Task(
        description="Verify the analyst signal. Define the exact Stop-Loss and Target Price.",
        agent=risk_manager,
        expected_output="Final approved trade plan: Signal, Entry, SL, and Target."
    )

    return Crew(
        agents=[analyst, risk_manager], 
        tasks=[analysis_task, risk_task], 
        process=Process.sequential
    )
