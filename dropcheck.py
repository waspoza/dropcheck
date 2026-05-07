import os, time
from datetime import datetime
import pandas as pd 
from selenium import webdriver 
from selenium.webdriver import Chrome 
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import smtplib, ssl
import logging, sys

mail_lines = []

def check_for_drops(url):
    driver.get(url)
    time.sleep(2)

    # send 3 page downs to load more channels
    for x in range(3):
        html = driver.find_element(By.TAG_NAME, 'html')
        html.send_keys(Keys.END)
        time.sleep(1)

    num_drops = 0
    lines = []
    global mail_lines, log

    log.debug(f"👉👉👉entering check_for_drops with url: {url}")
    articles = driver.find_elements(By.TAG_NAME, "article")
    if articles:
        for art in articles:
            try:
                a = art.find_element(By.TAG_NAME, "a")
                label = a.get_attribute("aria-label")
                href = a.get_attribute("href")
                log.debug(f"label: {label}")
                if "drops" in label.lower():
                    # check ignore list
                    if "metaphors" in href:
                        continue
                    lines.append(label)
                    lines.append(href)
                    num_drops += 1
                    log.debug(f"➕added above label. number of drops = {num_drops}")
            except Exception as e: 
                log.debug(f"‼️ got exception: {e}")
                continue
        # dont send mail if number of streams with drops is less than 3
        if num_drops > 3:
            mail_lines.extend(lines)
            log.debug(f"num drops above 3, mail_lines: {mail_lines}")
        else: 
            log.debug(f"num drops below 3")
    else:
        mail_lines.append("No articles!")

def setup_logging():
    logger = logging.getLogger('dropcheck')
    for h in logger.handlers:
      logger.removeHandler(h)

    h = logging.StreamHandler(sys.stdout)

    # use whatever format you want here
    FORMAT = '%(levelname)s: %(message)s'
    h.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

    return logger

logging.getLogger("requests").setLevel(logging.WARNING)

log = setup_logging()
#log.setLevel(logging.DEBUG)

 
# Define the Chrome webdriver options
options = webdriver.ChromeOptions()
options.add_argument("--headless") # Set the Chrome webdriver to run in headless mode for scalability

# By default, Selenium waits for all resources to download before taking actions.
# However, we don't need it as the page is populated with dynamically generated JavaScript code.
options.page_load_strategy = "none"
options.binary_location = "/home/piotr/chrome_driver/chrome-linux64/chrome"
service = Service("/home/piotr/chrome_driver/chromedriver-linux64/chromedriver")
# Pass the defined options objects to initialize the web driver
driver = Chrome(service=service, options=options)
# Set an implicit wait of 5 seconds to allow time for elements to appear before throwing an exception
driver.implicitly_wait(2)
#url = "https://www.twitch.tv/directory/category/overwatch-2"
urls = ["https://www.twitch.tv/directory/category/hearthstone", "https://www.twitch.tv/directory/category/world-of-warcraft", "https://www.twitch.tv/directory/category/warcraft-arclight-rumble"]

# exclude checking when you are aware and promotion is still ongoing
#              end date              url substring
excludes = [(datetime(2026, 5, 22), "world"),
            (datetime(2026, 3, 15), "hearth")]

today = datetime.now()
for url in urls:
    for exclude in excludes:
        if (today <= exclude[0] and exclude[1] in url):
            break
    else:
        check_for_drops(url)

log.debug(f"mail_lines lenngth: {len(mail_lines)}")
from secrets import username, password, smtp_server, sender_email, receiver_email
#if False:
if mail_lines:
    log.debug(f"☀️ got some mail lines")
    mail_txt = "Subject: Drops were found!\n\n"
    for i, line in enumerate(mail_lines):
        mail_txt += line + "\n"
        if i % 2:
            mail_txt += "\n"

    port = 465  # For SSL

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(username, password)
        server.sendmail(sender_email, receiver_email, mail_txt.encode('utf-8'))

    log.debug(f"mail: {mail_txt}")

#print(driver.page_source)
