from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import logging

class InstagramBot:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome()
        self.base_url = "https://www.instagram.com/"
        self.api_url = "http://localhost:3000"
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def login(self):
        try:
            self.driver.get(f"{self.base_url}accounts/login/")
            time.sleep(3)  # Wait for page load
            
            # Login
            username_field = self.driver.find_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            time.sleep(5)  # Wait for login
            
            self.logger.info("Login successful")
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            raise

    def navigate_to_inbox(self):
        try:
            self.driver.get(f"{self.base_url}direct/inbox/")
            time.sleep(5)  # Wait for inbox to load
            
            # Handle notification popup if it appears
            try:
                not_now = self.driver.find_element(By.XPATH, "")
                not_now.click()
            except:
                pass
                
            self.logger.info("Navigated to inbox")
        except Exception as e:
            self.logger.error(f"Failed to navigate to inbox: {e}")
            raise

    def get_response_from_server(self, query):
        try:
            payload = {
                "username": self.username,
                "query": query
            }
            
            response = requests.post(
                f"{self.api_url}/query",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                self.logger.error(f"Server returned status code: {response.status_code}")
                return "Sorry, I'm having trouble processing your request."
                
        except Exception as e:
            self.logger.error(f"Failed to get response from server: {e}")
            return "Sorry, I'm experiencing technical difficulties."

    def process_messages(self):
        try:
            # Wait for chats to load
            time.sleep(3)
            
            # Find all chat threads
            chats = self.driver.find_elements(By.XPATH, "//div[@role='listbox']/div")
            
            self.logger.info(f"Found {len(chats)} chats in inbox.")
            
            for chat in chats:
                try:
                    # Click the chat
                    chat.click()
                    time.sleep(2)
                    
                    # Get all messages
                    messages = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'x78zum5')]//span[contains(@class, 'xeuugli x18c0a79 xu37r0v x1fj9vlw x13faqbe x1vvkbs x14g2gp5 xuwz08h x1fxoii6 xrxb4jq xjff08q x1t1hd0b xvpol1d x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xnfyia')]")
                    
                    if not messages:
                        self.logger.info("No messages found in this chat.")
                        continue
                        
                    # Get last message
                    last_message = messages[-1].text
                    self.logger.info(f"Last message in chat: {last_message}")
                    
                    # Get sender name
                    sender_name = self.driver.find_element(By.XPATH, "//div[@role='button']//span[contains(@class, 'x193iq5w')]").text
                    self.logger.info(f"Sender: {sender_name}")
                    
                    # Only respond if it's a new message
                    if last_message:
                        print(f"Received message from {sender_name}: {last_message}")  # Print the message
                        self.logger.info(f"Got message from {sender_name}: {last_message}")
                        
                        # Get response from server
                        response = self.get_response_from_server(last_message)
                        
                        # Find message input and send response
                        try:
                            message_input = self.driver.find_element(By.XPATH, "//p[@class='xat24cr xdj266r']")
                            message_input.click()
                            message_input.send_keys(response)
                            message_input.send_keys(Keys.RETURN)
                            
                            print(f"Sent response to {sender_name}: {response}")  # Print response
                            self.logger.info(f"Sent response to {sender_name}: {response}")
                        except Exception as e:
                            self.logger.error(f"Failed to send response: {e}")
                            print(f"Error sending response: {e}")
                        
                        time.sleep(2)
                
                except Exception as e:
                    self.logger.error(f"Error processing chat: {e}")
                    print(f"Error processing chat: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error in process_messages: {e}")
            print(f"Error in process_messages: {e}")

    def run(self):
        try:
            self.login()
            self.navigate_to_inbox()
            
            while True:
                try:
                    self.process_messages()
                    time.sleep(10)  # Wait before checking messages again
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error(f"Error in main loop: {e}")
                    time.sleep(30)  # Wait longer before retrying after error
                    
        finally:
            self.driver.quit()
            self.logger.info("Bot stopped")

if __name__ == "__main__":
    USERNAME = "jestorshaunak"
    PASSWORD = "26314921*bubu"
    
    bot = InstagramBot(USERNAME, PASSWORD)
    bot.run()