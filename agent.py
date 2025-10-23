from dotenv import load_dotenv
from openai import OpenAI
import json
from CompanyInfo import get_company_info
from SearchSymbol import search_symbol
from StockPriceInfo import get_stock_price
from prompt import SYSTEM_PROMPT

load_dotenv()

client = OpenAI()

available_tools = {
    "get_stock_price": get_stock_price,
    "get_company_info": get_company_info,
    "search_symbol": search_symbol
}


print("\n\n🔔 Trading Agent - Ask me about stocks!\n")

message_history = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

user_query = input("👉 ")
message_history.append({"role": "user", "content": user_query})

while True:
    response = client.chat.completions.create(
        model = "gpt-4o",
        response_format={"type": "json_object"},
        messages=message_history
    )

    raw_result = response.choices[0].message.content
    message_history.append({"role": "assistant" , "content": raw_result})
    parsed_result = json.loads(raw_result)

    if parsed_result.get("step") == "START":
        print("🔥", parsed_result.get("content"))
        continue

    if parsed_result.get("step") == "TOOL":
        tool_to_call = parsed_result.get("tool")
        tool_input = parsed_result.get("input")
        print(f"⚒️  {tool_to_call}({tool_input})")

        tool_response = available_tools[tool_to_call](tool_input)
        print(f"📊 {tool_to_call}({tool_input}) = {tool_response}")
        message_history.append({"role": "developer", "content": json.dumps({"step": "OBSERVE", "tool": tool_to_call, "input": tool_input, "output": tool_response})})
        continue

    if parsed_result.get("step") == "PLAN":
        print("🧠", parsed_result.get("content"))
        continue

    if parsed_result.get("step") == "OUTPUT":
        print("🎁", parsed_result.get("content"))
        break

print("\n\n")

