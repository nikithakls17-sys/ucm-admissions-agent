from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup

mcp = FastMCP("ucm-admissions")

@mcp.tool()
def get_application_deadlines() -> str:
    """
    Fetch undergraduate application deadlines from the UCM admissions website.
    Returns detailed information about application deadlines and requirements.
    """
    print("[DEBUG] Tool called: get_application_deadlines", flush=True)
    url = "https://www.ucmo.edu/future-students/admissions/"
    try:
        print(f"[DEBUG] Fetching URL: {url}", flush=True)
        response = requests.get(url, timeout=10)
        print(f"[DEBUG] Response status: {response.status_code}", flush=True)
        
        if response.status_code != 200:
            return f"Unable to fetch admissions page. Status code: {response.status_code}"

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract all text content
        text = soup.get_text(separator="\n", strip=True)
        print(f"[DEBUG] Extracted {len(text)} characters of text", flush=True)
        
        # Look for deadline-related content
        lines = text.split('\n')
        relevant_info = []
        
        keywords = ['deadline', 'apply', 'application', 'fall', 'spring', 'summer', 
                   'freshman', 'transfer', 'admission', 'priority', 'date']
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords):
                # Include context (previous and next lines)
                context_start = max(0, i-1)
                context_end = min(len(lines), i+2)
                context = lines[context_start:context_end]
                relevant_info.extend(context)
        
        print(f"[DEBUG] Found {len(relevant_info)} relevant lines", flush=True)
        
        if relevant_info:
            # Remove duplicates while preserving order
            seen = set()
            unique_info = []
            for item in relevant_info:
                if item not in seen and len(item.strip()) > 0:
                    seen.add(item)
                    unique_info.append(item)
            
            result = "UCM Admissions Information:\n\n" + "\n".join(unique_info[:50])  # Limit to 50 lines
            print(f"[DEBUG] Returning result with {len(result)} characters", flush=True)
            return result
        
        return "Could not find specific deadline information. Please visit https://www.ucmo.edu/future-students/admissions/ directly."
        
    except Exception as e:
        error_msg = f"Error fetching admissions data: {str(e)}"
        print(f"[DEBUG] {error_msg}", flush=True)
        return error_msg

if __name__ == "__main__":
    # Use run() for stdio communication
    mcp.run()