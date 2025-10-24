from dotenv import load_dotenv
from openai import OpenAI
import json
from CompanyInfo import get_company_info
from SearchSymbol import search_symbol
from StockPriceInfo import get_stock_price
from prompt import SYSTEM_PROMPT
from pydantic import BaseModel, Field
from typing import Optional

load_dotenv()

client = OpenAI()

available_tools = {
    "get_stock_price": get_stock_price,
    "get_company_info": get_company_info,
    "search_symbol": search_symbol
}

class MyOutputFormat(BaseModel):
    step: str = Field(..., description="The ID of the step. Example: START, PLAN, OUTPUT, TOOL, OBSERVE")
    content: Optional[str] = Field(None, description="The optional string content for the step")
    tool: Optional[str] = Field(None, description="The ID of the tool to call (e.g., get_stock_price, get_company_info, search_symbol)")
    input: Optional[str] = Field(None, description="The input params for the tool (stock symbol or company name)")
    output: Optional[str] = Field(None,description="Output of the tool - JSON stringified if structured data")

print("\n\n🔔 Trading Agent - Ask me about stocks!\n")

message_history = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

user_query = input("👉 ")
message_history.append({"role": "user", "content": user_query})

while True:
    response = client.chat.completions.parse(
        model = "gpt-4o",
        response_format=MyOutputFormat,
        messages=message_history
    )

    raw_result = response.choices[0].message.content
    message_history.append({"role": "assistant" , "content": raw_result})
    parsed_result = response.choices[0].message.parsed

    if parsed_result.step == "START":
        print("🔥", parsed_result.content)
        continue

    if parsed_result.step == "TOOL":
        tool_to_call = parsed_result.tool
        tool_input = parsed_result.input
        print(f"⚒️  {tool_to_call}({tool_input})")

        tool_response = available_tools[tool_to_call](tool_input)
        print(f"📊 {tool_to_call}({tool_input}) = {tool_response}")
        message_history.append({"role": "developer", "content": json.dumps({"step": "OBSERVE", "tool": tool_to_call, "input": tool_input, "output": tool_response})})
        continue

    if parsed_result.step == "PLAN":
        print("🧠", parsed_result.content)
        continue

    if parsed_result.step == "OUTPUT":
        print("🎁", parsed_result.content)
        break

print("\n\n")

