from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

import Connect_Insta_LLM as CIL


class InstagramBot:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome()
        self.base_url = "https://www.instagram.com/"

    def human_like_write(self, message_box, message_text):
        for char in message_text:
            message_box.send_keys(char)
            time.sleep(random.uniform(0.001, 0.003))
    
    def login(self):
        try:
            self.driver.get(f"{self.base_url}accounts/login/")
            wait = WebDriverWait(self.driver, 10)
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            time.sleep(3)
            
            # Wait for home page to load
            wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'/direct/inbox/')]")))
            print("Login successful.")
        except Exception as e:
            print(f"An error occurred during login: {e}")
    
    def navigate_to_chats(self):
        try:
            time.sleep(4)
            self.driver.get(f"{self.base_url}direct/inbox/?next=%2F&hl=en")
            time.sleep(4)
            # After entering "messages", a pop show up everytime. It asks to allow notifications.
            # Below 2 lines are to press "Not Now" in the pop up.
            not_now = self.driver.find_element(By.XPATH, "//button[text()='Not Now']")
            not_now.click()
            print("Navigated to chat inbox.")
            time.sleep(8)
        except Exception as e:
            print(f"An error occurred while navigating to chats: {e}")

    # To get generated message and send it to the user
    def send_message(self, recipient, message):
        try:
            # Fetching response from the RAG LLM
            response = CIL.connector(recipient, message)
            
            message_box = self.driver.find_element(By.XPATH, ".//p[@class='xat24cr xdj266r']")
            message_box.click()
            self.human_like_write(message_box, response)
            message_box.send_keys(Keys.RETURN)
            
            print(f'"{response}" sent to {recipient} one his query "{message}".')
        except Exception as e:
            print(f"An error occurred while sending a message to {recipient}: {e}")            
    
    def check_new_messages(self):
        try:
            class_name_for_chat = 'x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x2lah0s xe8uvvx x2lwn1j xeuugli x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1q0g3np x87ps6o x1lku1pv x1a2a7pz x168nmei x13lgxp2 x5pf9jr xo71vjh x1lliihq xdj266r x11i5rnm xat24cr x1mh8g0r xg6hnt2 x18wri0h x1l895ks x1y1aw1k xwib8y2 xbbxn1n xxbr6pl'
            incoming_msg_class="x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x41vudc x6prxxf xvq8zen xo1l8bm xzsf02u"
            chat_elements = self.driver.find_elements(By.XPATH, f"//div[@class='{class_name_for_chat}']")
            for chat in chat_elements:
                chat.click()
                time.sleep(3)
                msgs = self.driver.find_elements(By.XPATH, f"//div[@class='x78zum5 xdt5ytf']")  # Gets all the messages
                flag = True    # Will turn the flag to False if the chat is empty or the last message is not by the user (i.e., it is by bot)
                
                if (msgs!=[]):
                    last_msg = msgs[-1]
                    try:
                        aa = last_msg.find_element(By.XPATH, f".//span[@class='{incoming_msg_class}']")
                        # To check if last message was sent by bot or by customer
                    except:  # If last message was by bot, the above line will give error
                        flag = False
                else:
                    flag = False
                
                if(flag):   # If flag==True, we need to reply
                    # Getting name of the user
                    name = self.driver.find_element(By.XPATH, "//span[@class='x1lliihq x193iq5w x6ikm8r x10wlt62 xlyipyv xuxw1ft']")
                    name = name.text

                    query = ''
                    i=-1

                    # Below loop is to get all unread messages.
                    while True:
                        try:
                            last_msg = msgs[i]
                            aa = last_msg.find_element(By.XPATH, f".//span[@class='{incoming_msg_class}']")
                            aa = aa.text
                            query = aa + query
                            i=i-1
                        except:
                            break
                    
                    bot.send_message(name, query)

        except Exception as e:
            bot.send_message(None, None)
            print(f"An error occurred while checking new messages: {e}")
    
    
    
    def close(self):
        self.driver.quit()
        print("Browser closed.")


if __name__ == "__main__":
    USERNAME = "jestorshaunak"
    PASSWORD = "26314921*bubu"
    
    bot = InstagramBot(USERNAME, PASSWORD)
    bot.login()
    bot.navigate_to_chats()

    # Keep running the bot unless interupted by keyboard
    while True:
        try:
            unread_chats = bot.check_new_messages()
        except:
            bot.close()
            break