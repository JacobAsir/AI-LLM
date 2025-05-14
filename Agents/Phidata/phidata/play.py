from phi.agent import Agent
import phi.api
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools
from phi.tools.duckduckgo import DuckDuckGo

import phi
from phi.playground import Playground, serve_playground_app
import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["PHIDATA_API_KEY"] = os.getenv("PHIDATA_API_KEY")

web_search_agent = Agent(
    name = "web search agent",
    role = "search the web for the information",
    model = Groq(id = "llama3-70b-8192"),
    tools = [DuckDuckGo()],
    instructions = ["Always include sources"],
    show_tools_calls = True,
    markdoewn = True, 
)

yinance_agent = Agent(
    name = "finance agent",
    model = Groq(id = "llama3-70b-8192"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, stock_fundamentals=True,
            company_news = True)],
    show_tool_calls=True,
    instructions=["Use tables to display data"],
    markdown = True,
)

app = Playground(agents = [web_search_agent, yinance_agent]).get_app()

if __name__=="__main__":
    serve_playground_app("playground:app", reload = True)