from dotenv import load_dotenv
import requests
import os

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

if not ALPHA_VANTAGE_API_KEY:
    print("⚠️  Warning: ALPHA_VANTAGE_API_KEY not found in .env file")
    print("Get your free API key from: https://www.alphavantage.co/support/#api-key")
    print("Add it to your .env file as: ALPHA_VANTAGE_API_KEY=your_key_here\n")


def search_symbol(company_name: str):
    """Search for stock symbol by company name"""
    url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={company_name}&apikey={ALPHA_VANTAGE_API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            if "Note" in data:
                return {"error": "API rate limit reached. Please wait a minute and try again."}
            
            matches = data.get('bestMatches', [])
            
            if matches:
                results = []
                for match in matches[:5]:  # Return top 5 matches
                    results.append({
                        "symbol": match.get('1. symbol', 'N/A'),
                        "name": match.get('2. name', 'N/A'),
                        "type": match.get('3. type', 'N/A'),
                        "region": match.get('4. region', 'N/A')
                    })
                return {"results": results}
            else:
                return {"error": f"No results found for '{company_name}'"}
        
        return {"error": "Could not perform search"}
    except Exception as e:
        return {"error": f"Error searching: {str(e)}"}

# symbol = search_symbol("apple")
