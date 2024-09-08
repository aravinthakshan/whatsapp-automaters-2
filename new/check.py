

import csv
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_phone_numbers(file_path):
    phone_numbers = []
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row:
                    phone_number = row[1].strip()
                    if not phone_number.startswith('+91'):
                        phone_number = '+91' + phone_number
                    phone_numbers.append(phone_number)
        logging.info(f"Successfully read {len(phone_numbers)} phone numbers from {file_path}")
    except Exception as e:
        logging.error(f"Failed to read phone numbers: {str(e)}")
    return phone_numbers
message = """Thank you for registering for Mars Rover Manipal. 
Join this WhatsApp Community for further details:
Link to the MRM 2025-26 Recruitment Community: https://chat.whatsapp.com/GHlXB5kwLdr8b6HzhxsyL1"""

message = """Thank you for registering for Mars Rover Manipal. 
Join this WhatsApp Community for further details:
Link to the MRM 2025-26 Recruitment Community: https://chat.whatsapp.com/GHlXB5kwLdr8b6HzhxsyL1"""

def send_bulk_message(phone_numbers, message, use_firefox=False):
    driver = None
    try:
        if use_firefox:
            options = FirefoxOptions()
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            logging.info("Using Firefox WebDriver")
        else:
            options = ChromeOptions()
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            logging.info("Using Chrome WebDriver with GPU disabled")
        
        wait = WebDriverWait(driver, 60)
        driver.get('https://web.whatsapp.com')
        logging.info("Opened WhatsApp Web")

        input("Scan the QR code and press Enter once logged in...")
        logging.info("User confirmed login")

        for phone in phone_numbers:
            try:
                url = f"https://web.whatsapp.com/send?phone={phone}&text={message}"
                driver.get(url)
                logging.info(f"Navigated to chat for {phone}")

                # Wait for the chat to load
                chat_loaded = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="conversation-panel-messages"]')))
                logging.info("Chat loaded")

                # Wait for user confirmation before proceeding
                input(f"Please confirm that the chat for {phone} is loaded and the message is in the text box. Press Enter to continue...")

                # Try to find the send button
                try:
                    send_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]')))
                    logging.info("Send button found")
                    send_button.click()
                    logging.info("Clicked send button")
                except (TimeoutException, ElementNotInteractableException):
                    logging.info("Send button not clickable, trying Enter key")
                    input_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@title="Type a message"]')))
                    input_box.send_keys(Keys.ENTER)
                    logging.info("Sent message using Enter key")

                # Wait for user confirmation that the message was sent
                input("Please confirm that the message was sent successfully. Press Enter to continue to the next number...")
                
                logging.info(f"User confirmed message sent to {phone}")

            except TimeoutException:
                logging.warning(f"Timeout occurred for {phone}. Moving to next number.")
            except NoSuchElementException:
                logging.warning(f"Failed to locate element for {phone}. Moving to next number.")
            except Exception as e:
                logging.error(f"Failed to send message to {phone}: {str(e)}")

    except Exception as e:
        logging.error(f"An error occurred in the main sending process: {str(e)}")
    finally:
        if driver:
            driver.quit()
            logging.info("WebDriver closed")

if __name__ == "__main__":
    phone_numbers = read_phone_numbers('numbers.csv')
    if phone_numbers:
        use_firefox = input("Do you want to use Firefox instead of Chrome? (y/n): ").lower() == 'y'
        send_bulk_message(phone_numbers, message, use_firefox)
    else:
        logging.warning("No phone numbers found.")