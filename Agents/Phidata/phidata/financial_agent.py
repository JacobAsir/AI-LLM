from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools
from phi.tools.duckduckgo import DuckDuckGo
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["PHIDATA_API_KEY"] = os.getenv("PHIDATA_API_KEY")

# Initialize agents
web_search_agent = Agent(
    name="web search agent",
    role="search the web for the information",
    model=Groq(id="llama3-70b-8192"),
    tools=[DuckDuckGo()],
    instructions=["Always include sources"],
    show_tools_calls=True,
    markdown=True,
)

yinance_agent = Agent(
    name="finance agent",
    model=Groq(id="llama3-70b-8192"),
    tools=[YFinanceTools(
        stock_price=True,
        analyst_recommendations=True,
        stock_fundamentals=True,
        company_news=True
    )],
    show_tools_calls=True,
    instructions=["Use tables to display data"],
    markdown=True,
)

multi_ai_agent = Agent(
    team=[web_search_agent, yinance_agent],
    instructions=["Always include sources", "Use tables to display data"],
    show_tools_calls=True,
    markdown=True,
)


multi_ai_agent.print_response("Summarize analyst recommendation and share the latest news for NVDA")