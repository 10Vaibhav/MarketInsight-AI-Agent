import streamlit as st
from openai import OpenAI
import json
import os
from CompanyInfo import get_company_info
from SearchSymbol import search_symbol
from StockPriceInfo import get_stock_price
from prompt import SYSTEM_PROMPT
from PIL import Image


st.set_page_config(
    page_title="Trade Agent",
    page_icon="public/images/icon.jpg",
    layout="centered"
)


st.markdown("""
    <style>
    .stChat [data-testid="chatAvatarIcon-user"] {
        background-color: #4CAF50;
    }
    .stChat [data-testid="chatAvatarIcon-assistant"] {
        background-color: #2196F3;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "api_keys_set" not in st.session_state:
    st.session_state.api_keys_set = False
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ""
if "alpha_vantage_api_key" not in st.session_state:
    st.session_state.alpha_vantage_api_key = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "client" not in st.session_state:
    st.session_state.client = None

# Available tools dictionary
available_tools = {
    "get_stock_price": get_stock_price,
    "get_company_info": get_company_info,
    "search_symbol": search_symbol
}

# Check if API keys are set
if not st.session_state.api_keys_set:
    st.title("🔐 API Configuration")
    st.markdown("Please enter your API keys to use the Trading Agent")

    with st.form("api_keys_form"):
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Get your API key from https://platform.openai.com/api-keys"
        )

        alpha_vantage_key = st.text_input(
            "Alpha Vantage API Key",
            type="password",
            placeholder="Your Alpha Vantage API key",
            help="Get your free API key from https://www.alphavantage.co/support/#api-key"
        )

        submitted = st.form_submit_button("🚀 Start Trading Agent")

        if submitted:
            if openai_key.strip() and alpha_vantage_key.strip():
                # Set API keys in session state
                st.session_state.openai_api_key = openai_key.strip()
                st.session_state.alpha_vantage_api_key = alpha_vantage_key.strip()

                # Set environment variables
                os.environ["OPENAI_API_KEY"] = st.session_state.openai_api_key
                os.environ["ALPHA_VANTAGE_API_KEY"] = st.session_state.alpha_vantage_api_key

                try:
                    st.session_state.client = OpenAI(api_key=st.session_state.openai_api_key)

                    st.session_state.messages = [
                        {"role": "system", "content": SYSTEM_PROMPT}
                    ]
                    st.session_state.chat_history = []

                    st.session_state.api_keys_set = True
                    st.success("✅ API keys configured successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error initializing OpenAI client: {str(e)}")
            else:
                st.error("⚠️ Please enter both API keys")

    # Information section
    st.markdown("---")
    title_image = Image.open("public/images/how.jpg") 
    st.image(title_image, width=250, use_container_width=False, output_format="JPG")
    st.title("How to get API Keys?")
    st.markdown("""
    **OpenAI API Key:**
    1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
    2. Sign in or create an account
    3. Click "Create new secret key"
    4. Copy and paste the key above

    **Alpha Vantage API Key:**
    1. Go to [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
    2. Enter your email and organization
    3. Click "GET FREE API KEY"
    4. Copy and paste the key above

    *Note: Your API keys are stored only in your current session and are not saved permanently.*
    """)

else:
    # Main app interface
    title_image = Image.open("public/images/trading agent.jpg") 
    st.image(title_image, width=450, use_container_width=False, output_format="JPG")
    st.markdown("Ask me about stocks!")


    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    if prompt := st.chat_input("Ask about a stock..."):

        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "user", "content": prompt})


        with st.chat_message("user"):
            st.markdown(prompt)


        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            while True:
                try:
                    response = st.session_state.client.chat.completions.create(
                        model="gpt-4o",
                        response_format={"type": "json_object"},
                        messages=st.session_state.messages
                    )

                    raw_result = response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": raw_result})
                    parsed_result = json.loads(raw_result)

                    # Handle START step
                    if parsed_result.get("step") == "START":
                        content = parsed_result.get("content")
                        full_response += f"🔥 {content}\n\n"
                        message_placeholder.markdown(full_response)
                        continue

                    if parsed_result.get("step") == "TOOL":
                        tool_to_call = parsed_result.get("tool")
                        tool_input = parsed_result.get("input")

                        full_response += f"⚒️ Calling {tool_to_call}({tool_input})\n\n"
                        message_placeholder.markdown(full_response)

                        tool_response = available_tools[tool_to_call](tool_input)
                        full_response += f"📊 {tool_to_call} returned: {tool_response}\n\n"
                        message_placeholder.markdown(full_response)

                        st.session_state.messages.append({
                            "role": "developer",
                            "content": json.dumps({
                                "step": "OBSERVE",
                                "tool": tool_to_call,
                                "input": tool_input,
                                "output": tool_response
                            })
                        })
                        continue

                    if parsed_result.get("step") == "PLAN":
                        content = parsed_result.get("content")
                        full_response += f"🧠 {content}\n\n"
                        message_placeholder.markdown(full_response)
                        continue

                    if parsed_result.get("step") == "OUTPUT":
                        content = parsed_result.get("content")
                        full_response += f"🎁 {content}"
                        message_placeholder.markdown(full_response)
                        break

                except Exception as e:
                    full_response += f"\n\n❌ Error: {str(e)}"
                    message_placeholder.markdown(full_response)
                    break

            st.session_state.chat_history.append({"role": "assistant", "content": full_response})

    with st.sidebar:
        st.header("About")
        st.markdown("""
        This Trading Agent can help you with:
        - 💵 Stock prices
        - 📑 Company information
        - 🔍 Symbol search

        Just ask a question about any stock!
        """)

        if st.button("🔄 Clear Chat History"):
            st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            st.session_state.chat_history = []
            st.rerun()

        if st.button("🔑 Reset API Keys"):
            st.session_state.api_keys_set = False
            st.session_state.openai_api_key = ""
            st.session_state.alpha_vantage_api_key = ""
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.session_state.client = None
            st.rerun()

        st.markdown("---")
        st.markdown("**Example queries:**")
        st.markdown("- What's the price of AAPL?")
        st.markdown("- Tell me about Tesla")
        st.markdown("- Search for Microsoft symbol")

        st.markdown("---")
        st.caption("🔐 API keys are active for this session")
