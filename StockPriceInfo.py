from dotenv import load_dotenv
import requests
import os

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

if not ALPHA_VANTAGE_API_KEY:
    print("⚠️  Warning: ALPHA_VANTAGE_API_KEY not found in .env file")
    print("Get your free API key from: https://www.alphavantage.co/support/#api-key")
    print("Add it to your .env file as: ALPHA_VANTAGE_API_KEY=your_key_here\n")



def get_stock_price(symbol: str):
    """Get current stock price for a given symbol using Alpha Vantage"""
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol.upper()}&apikey={ALPHA_VANTAGE_API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
    
            # Check for API error messages
            if "Error Message" in data:
                return {"error": f"Invalid symbol: {symbol}"}
            
            if "Note" in data:
                return {"error": "API rate limit reached. Please wait a minute and try again."}
            
            quote = data.get('Global Quote', {})
            
            if quote:
                current_price = float(quote.get('05. price', 0))
                previous_close = float(quote.get('08. previous close', 0))
                change = float(quote.get('09. change', 0))
                change_percent = quote.get('10. change percent', '0%').replace('%', '')
                
                return {
                    "symbol": symbol.upper(),
                    "price": round(current_price, 2),
                    "previous_close": round(previous_close, 2),
                    "change": round(change, 2),
                    "change_percent": change_percent,
                    "volume": quote.get('06. volume', 'N/A'),
                    "latest_trading_day": quote.get('07. latest trading day', 'N/A')
                }
        
        return {"error": f"Could not fetch stock data for {symbol}"}
    except Exception as e:
        return {"error": f"Error fetching stock data: {str(e)}"}


# data_structured = get_stock_price("AAPL")
