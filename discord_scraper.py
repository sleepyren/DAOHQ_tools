from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import datetime
import re
import pymongo
from decouple import config
from fake_useragent import UserAgent
import time

def get_driver_instance():
    ua = UserAgent()
    s = Service('/home/worthyrae/Development/daohq/DAOHQ-ops/chromedriver')
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={ua.random}')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('headless')                        
    driver = webdriver.Chrome(options=options)
    return driver

def create_mongo_client():
    try:
        client = pymongo.MongoClient(config('DB_URL'), serverSelectionTimeoutMS=5000)
        client.server_info()
        return client
    except pymongo.errors.ServerSelectionTimeoutError as err:
        return None
      
def get_discord_members(url, driver):
    if url != None:
        driver.get(url)
        try:
            element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Members')]"))
            )
            soup = BeautifulSoup(driver.page_source, 'lxml')
            items = soup.find_all('span', attrs={'class': re.compile('^pillMessage.*')})
            online_members = int(re.sub('[^0-9]', '', str(items[0].text)))
            total_members = int(re.sub('[^0-9]', '', str(items[1].text)))
            timestamp = datetime.datetime.now()
            driver.quit()
            return online_members, total_members, timestamp
        except:
            timestamp = datetime.datetime.now()
            driver.quit()
            return None, None, timestamp
    timestamp = datetime.datetime.now()
    return None, None, timestamp

def initialize():
    client = create_mongo_client()
    if client != None:
        dao_updates = []
        dao_historical_updates = []
        dao_dict = {}
        for dao in client.main.daos.find({'discord': {'$ne': None}}):
            dao_dict[dao['_id']] = dao['discord']
        for dao_id, dao_discord in dao_dict.items():
            if dao_discord[:4] == 'http' and 'discord' in dao_discord:
                driver = get_driver_instance()
                online_members, total_members, timestamp = get_discord_members(dao_discord, driver)
                if online_members == None and total_members == None:
                    pass
                else:
                    historic_records = list(client.main.dao.historicaldiscord.find({'dao': dao_id}).sort('lastUpdated', -1))
                    if len(historic_records) == 0:
                        percentChange24h = 0
                        percentChange7d = 0
                        percentChange30d = 0
                    elif len(historic_records) < 24:
                        percentChange24h = total_members / historic_records[len(historic_records)-1]['totalMembers'] - 1
                        percentChange7d = total_members / historic_records[len(historic_records)-1]['totalMembers'] - 1
                        percentChange30d = total_members / historic_records[len(historic_records)-1]['totalMembers'] - 1
                    elif len(historic_records) < 168:
                        percentChange24h = total_members / historic_records[23]['totalMembers'] - 1
                        percentChange7d = total_members / historic_records[len(historic_records)-1]['totalMembers'] - 1
                        percentChange30d = total_members / historic_records[len(historic_records)-1]['totalMembers'] - 1
                    elif len(historic_records) < 720:
                        percentChange24h = total_members / historic_records[23]['totalMembers'] - 1
                        percentChange7d = total_members / historic_records[167]['totalMembers'] - 1
                        percentChange30d = total_members / historic_records[len(historic_records)-1]['totalMembers'] - 1
                    else:
                        percentChange24h = total_members / historic_records[23]['totalMembers'] - 1
                        percentChange7d = total_members / historic_records[167]['totalMembers'] - 1
                        percentChange30d = total_members / historic_records[719]['totalMembers'] - 1
                    dao_updates.append(pymongo.UpdateOne({'_id': dao_id}, {'$set': {'discordData.totalMembers': total_members, 'discordData.activeMembers': online_members, 'discordData.percentChange24h': percentChange24h, 'discordData.percentChange7d': percentChange7d, 'discordData.percentChange30d': percentChange30d, 'discordData.lastUpdated': timestamp}}))
                    dao_historical_updates.append(pymongo.InsertOne({'dao': dao_id, 'totalMembers': total_members, 'activeMembers': online_members, 'lastUpdated': timestamp}))
        if len(dao_updates) > 0:
            dao_results = client.main.daos.bulk_write(dao_updates)
        if len(dao_historical_updates) > 0:
            dao_historical_results = client.main.dao.historicaldiscord.bulk_write(dao_historical_updates)
    else:
        time.sleep(5)
        initialize()
        
if __name__ == '__main__':
    initialize()


