from datetime import datetime
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
from pymongo import MongoClient

# driver starts

chrome_options = Options()
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--headless")

# on my system, relative driver path does not work (win10),
# but driver in the main folder works just fine

with webdriver.Chrome(options=chrome_options) as driver:
    driver.implicitly_wait(10)
    driver.get('https://e.mail.ru')
    actions = ActionChains(driver)

    # login

    element = driver.find_element(By.XPATH, '//input[@name = "username"]')
    element.send_keys('study.ai_172@mail.ru')
    element.send_keys(Keys.ENTER)

    element = driver.find_element(By.XPATH, '//input[@name = "password"]')
    element.send_keys('NextPassword172#')
    element.send_keys(Keys.ENTER)

    # getting unique messages' urls

    messages = set()

    # break condition: are messages the same as the time before?

    last_messages = []
    same_again = 0
    selector = '//a[contains(@class, "llc llc_normal")]'

    # scrolling down & collecting links

    while True:
        try:
            elements = driver.find_elements(By.XPATH, selector)

            # have we reached break condition (10 times to make sure)?

            if elements == last_messages:
                same_again += 1
                if same_again > 10:
                    break
            else:
                same_again = 0
                last_messages = elements[::]
                for element in elements:
                    link = element.get_attribute('href')
                    messages.add(link)

            # arrow down through collected links

            step = len(elements)-1
            for i in range(step):
                actions.send_keys(Keys.ARROW_DOWN)
                actions.perform()

                # improves spontaneous crashing

                time.sleep(0.05)
        except Exception:
            print("Scraping aborted suddenly for no reason!")
            break

    # retrieving messages info

    messages_info = []
    for message in messages:
        message_dict = {}
        driver.get(message)
        title = driver.find_element(By.CLASS_NAME, "thread-subject").text
        sender_element = driver.find_element(
            By.XPATH, "//span[@class = 'letter-contact']")
        sender = sender_element.get_attribute('title')
        datestring = driver.find_element(By.CLASS_NAME, "letter__date").text
        lines = driver.find_elements(By.CLASS_NAME, "letter-body")

        # brutally concatenating all text attributes within "letter-body"

        message_text = ''
        for line in lines:
            message_text += line.text

        message_dict['link'] = message
        message_dict['title'] = title
        message_dict['from'] = sender
        message_dict['datestring'] = datestring
        message_dict['text'] = message_text
        message_dict['current_date'] = datetime.today().strftime('%d-%m-%Y')

        messages_info.append(message_dict)

    # putting into db

    client = MongoClient('127.0.0.1', 27017)
    db = client['Mail_ru']
    if db.inbox == None:
        db.inbox.insert_many(messages_info)
    else:
        for item in messages_info:
            if not db.inbox.find_one({'link': item['link']}):
                db.inbox.insert_one(item)
