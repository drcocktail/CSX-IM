import requests
import json
import time
from typing import Optional

class LLMConnector:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.headers = {"Content-Type": "application/json"}
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def send_query(self, username: str, query: str) -> Optional[str]:
        """
        Send a query to the LLM server and get the response.
        
        Args:
            username (str): Instagram username of the sender
            query (str): The message/query from the user
            
        Returns:
            str: Response from the LLM server
            None: If there's an error in processing
        """
        payload = {
            "username": username,
            "query": query
        }

        for attempt in range(self.max_retries):
            try:
                # Send POST request to the server
                response = requests.post(
                    f"{self.base_url}/query",
                    json=payload,
                    headers=self.headers,
                    timeout=30  # 30 seconds timeout
                )
                
                # Check if request was successful
                response.raise_for_status()
                
                # Parse and return the response
                response_data = response.json()
                
                # Assuming the response JSON has a 'response' key
                # Modify this based on your actual API response structure
                return response_data.get('response', 'I apologize, but I couldn\'t process your request at the moment.')
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    print(f"Error connecting to LLM server after {self.max_retries} attempts: {e}")
                    return "I apologize, but I'm having trouble connecting to my backend service right now. Please try again later."
                
                print(f"Attempt {attempt + 1} failed. Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")
                return "I apologize, but I received an invalid response from the server. Please try again."
            
            except Exception as e:
                print(f"Unexpected error occurred: {e}")
                return "I apologize, but something unexpected went wrong. Please try again later."

# Create a singleton instance
_connector = LLMConnector()

def connector(username: str, message: str) -> str:
    """
    Main interface function to be used by the Instagram bot.
    
    Args:
        username (str): Instagram username of the sender
        message (str): The message to be processed
        
    Returns:
        str: Response from the LLM
    """
    if not username or not message:
        return "I apologize, but I couldn't process an empty message."
    
    response = _connector.send_query(username, message)
    return response if response else "I apologize, but I couldn't generate a response at this time."