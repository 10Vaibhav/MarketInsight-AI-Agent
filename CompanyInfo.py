from dotenv import load_dotenv
import requests
import os

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

if not ALPHA_VANTAGE_API_KEY:
    print("⚠️  Warning: ALPHA_VANTAGE_API_KEY not found in .env file")
    print("Get your free API key from: https://www.alphavantage.co/support/#api-key")
    print("Add it to your .env file as: ALPHA_VANTAGE_API_KEY=your_key_here\n")


def get_company_info(symbol: str):
    """Get company overview information using Alpha Vantage"""
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol.upper()}&apikey={ALPHA_VANTAGE_API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Check for API error messages
            if "Error Message" in data:
                return {"error": f"Invalid symbol: {symbol}"}
            
            if "Note" in data:
                return {"error": "API rate limit reached. Please wait a minute and try again."}
            
            if data and data.get('Symbol'):
                return {
                    "symbol": data.get('Symbol', 'N/A'),
                    "name": data.get('Name', 'N/A'),
                    "description": data.get('Description', 'N/A')[:300] + "..." if data.get('Description') else 'N/A',
                    "sector": data.get('Sector', 'N/A'),
                    "industry": data.get('Industry', 'N/A'),
                    "market_cap": data.get('MarketCapitalization', 'N/A'),
                    "pe_ratio": data.get('PERatio', 'N/A'),
                    "52_week_high": data.get('52WeekHigh', 'N/A'),
                    "52_week_low": data.get('52WeekLow', 'N/A')
                }
        
        return {"error": f"Could not fetch company info for {symbol}"}
    except Exception as e:
        return {"error": f"Error fetching company info: {str(e)}"}

# data_structured = get_company_info("AAPL")

