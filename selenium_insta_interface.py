from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import random
import logging
import Connect_Insta_LLM as CIL

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class InstagramBot:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome()
        self.base_url = "https://www.instagram.com/"
        self.wait = WebDriverWait(self.driver, 10)

    def human_like_write(self, message_box, message_text):
        """Simulate human-like typing with variable delays."""
        try:
            for char in message_text:
                message_box.send_keys(char)
                time.sleep(random.uniform(0.001, 0.003))
        except Exception as e:
            logging.error(f"Error in human-like typing: {e}")
            raise
    
    def login(self):
        """Handle Instagram login with improved error handling."""
        try:
            self.driver.get(f"{self.base_url}accounts/login/")
            
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            
            # Wait for successful login
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'/direct/inbox/')]"))
            )
            logging.info("Login successful")
            
        except TimeoutException:
            logging.error("Timeout during login - check internet connection or Instagram availability")
            raise
        except Exception as e:
            logging.error(f"Login failed: {e}")
            raise
    
    def navigate_to_chats(self):
        """Navigate to Instagram DM inbox with improved handling of notification popup."""
        try:
            time.sleep(2)  # Short delay before navigation
            self.driver.get(f"{self.base_url}direct/inbox/?next=%2F&hl=en")
            
            # Handle notification popup with explicit wait
            try:
                not_now_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now']"))
                )
                not_now_button.click()
            except TimeoutException:
                logging.info("Notification popup not found - continuing")
                
            # Wait for chat interface to load
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'x78zum5')]"))
            )
            logging.info("Successfully navigated to chat inbox")
            
        except Exception as e:
            logging.error(f"Error navigating to chats: {e}")
            raise

    def send_message(self, recipient, message):
        """Send message with improved error handling and logging."""
        try:
            if not recipient or not message:
                logging.warning("Attempted to send message with empty recipient or message")
                return

            # Get response from middleware
            response = CIL.connector(recipient, message)
            if not response:
                logging.error("Empty response received from LLM")
                return

            # Find and click message box
            message_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, ".//p[@class='xat24cr xdj266r']"))
            )
            message_box.click()
            
            # Type and send message
            self.human_like_write(message_box, response)
            message_box.send_keys(Keys.RETURN)
            
            logging.info(f'Message sent to {recipient} - Query: "{message}" - Response: "{response}"')
            time.sleep(1)  # Short delay after sending
            
        except Exception as e:
            logging.error(f"Error sending message to {recipient}: {e}")
            # Don't raise here to continue bot operation

    def check_new_messages(self):
        """Check for and process new messages with improved reliability."""
        try:
            # Class names for elements
            chat_class = 'x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x2lah0s xe8uvvx x2lwn1j xeuugli x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1q0g3np x87ps6o x1lku1pv x1a2a7pz x168nmei x13lgxp2 x5pf9jr xo71vjh x1lliihq xdj266r x11i5rnm xat24cr x1mh8g0r xg6hnt2 x18wri0h x1l895ks x1y1aw1k xwib8y2 xbbxn1n xxbr6pl'
            incoming_msg_class = "x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x41vudc x6prxxf xvq8zen xo1l8bm xzsf02u"

            # Find all chat elements
            chat_elements = self.driver.find_elements(By.XPATH, f"//div[@class='{chat_class}']")
            
            for chat in chat_elements:
                try:
                    # Click chat with retry mechanism
                    max_retries = 3
                    for _ in range(max_retries):
                        try:
                            chat.click()
                            break
                        except ElementClickInterceptedException:
                            time.sleep(1)
                    
                    time.sleep(2)  # Wait for messages to load
                    
                    # Get all messages in current chat
                    messages = self.wait.until(
                        EC.presence_of_all_elements_located((By.XPATH, "//div[@class='x78zum5 xdt5ytf']"))
                    )
                    
                    if not messages:
                        continue
                        
                    # Check if last message is from user
                    last_message = messages[-1]
                    try:
                        last_message.find_element(By.XPATH, f".//span[@class='{incoming_msg_class}']")
                    except NoSuchElementException:
                        continue  # Last message was from bot, skip
                        
                    # Get user's name
                    name = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//span[@class='x1lliihq x193iq5w x6ikm8r x10wlt62 xlyipyv xuxw1ft']"))
                    ).text
                    
                    # Collect all unread messages
                    query = []
                    for msg in reversed(messages):
                        try:
                            msg_text = msg.find_element(By.XPATH, f".//span[@class='{incoming_msg_class}']").text
                            query.append(msg_text)
                        except NoSuchElementException:
                            break
                    
                    if query:
                        # Join messages and send response
                        full_query = " ".join(reversed(query))
                        self.send_message(name, full_query)
                        
                except Exception as e:
                    logging.error(f"Error processing chat: {e}")
                    continue
                    
        except Exception as e:
            logging.error(f"Error checking new messages: {e}")
    
    def close(self):
        """Clean up resources."""
        try:
            self.driver.quit()
            logging.info("Browser closed successfully")
        except Exception as e:
            logging.error(f"Error closing browser: {e}")

if __name__ == "__main__":
    try:
        USERNAME = "jestorshaunak"
        PASSWORD = "26314921*bubu"
        
        bot = InstagramBot(USERNAME, PASSWORD)
        bot.login()
        bot.navigate_to_chats()

        # Main bot loop
        while True:
            try:
                bot.check_new_messages()
                time.sleep(5)  # Prevent excessive checking
            except KeyboardInterrupt:
                logging.info("Bot shutdown initiated by user")
                break
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(10)  # Longer delay on error
                
    except Exception as e:
        logging.critical(f"Critical error: {e}")
    finally:
        try:
            bot.close()
        except:
            pass