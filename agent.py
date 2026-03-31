from crewai import Agent, Task, Crew, Process

def create_trading_crew(stock_data):
    # Analyst Agent: Looks for patterns
    analyst = Agent(
        role='Technical Analyst',
        goal='Analyze price action and indicators to find entry points.',
        backstory="Expert in Indian equity markets with a focus on Nifty 50 stocks.",
        allow_delegation=False,
        verbose=True
    )

    # Risk Manager Agent: Essential for production to prevent blown accounts
    risk_manager = Agent(
        role='Risk Manager',
        goal='Evaluate trade signals and set strict Stop-Loss/Take-Profit levels.',
        backstory="Conservative risk officer. Never allows a trade without a 1:2 Risk-Reward ratio.",
        allow_delegation=True
    )

    analysis_task = Task(
        description=f"Analyze this data: {stock_data}. Provide a Buy/Sell/Hold recommendation.",
        agent=analyst,
        expected_output="A concise trading signal with technical justification."
    )

    risk_task = Task(
        description="Verify the analyst signal. Define the exact Stop-Loss and Target Price.",
        agent=risk_manager,
        expected_output="Final approved trade details including SL and Target."
    )

    return Crew(agents=[analyst, risk_manager], tasks=[analysis_task, risk_task], process=Process.sequential)
