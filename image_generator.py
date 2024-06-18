from PIL import Image, ImageFont, ImageDraw 
import textwrap
import pymongo
import random
from io import BytesIO
import requests
import os
import dotenv import load_dotenv
from numerize import numerize

MONGO_LINK = os.getenv("MONGO_LINK")
load_dotenv()

def create_mongo_client():
    try:
        client = pymongo.MongoClient(MONGO_LINK, serverSelectionTimeoutMS=5000)
        client.server_info()
        return client
    except pymongo.errors.ServerSelectionTimeoutError as err:
        return None

def get_dao():
    client = create_mongo_client()
    tokens = list(client.main.tokens.find({'live': True, 'livePrice': True, 'dao': { '$ne': None }}))
    i = random.randint(0,len(tokens) - 1)
    token = tokens[i]
    dao = client.main.daos.find_one({'_id': token['dao'], 'discordData.totalMembers': { '$exists': True }})
    if dao == None:
        create_image()
    return dao, token

def create_image():
    dao, token = get_dao()
    if dao['discordData']['totalMembers'] != None:
        base = Image.open("/Users/renaldohyacinthe/Downloads/istockphoto-1320330053-170667a.jpg")
        name = dao['name']
        description = dao['mission']
        percent_change_7d = token['financialData']['percentChange7d']
        positive = 0
        if percent_change_7d > 0:
            dir = Image.open("/Users/renaldohyacinthe/Downloads/istockphoto-1320330053-170667a.jpg")
            positive = 1
        else:
            dir = Image.open("/Users/renaldohyacinthe/Downloads/Trollface_non-free.png")
        dir = dir.resize((125,125))
        base.paste(dir, (500, 587))
        discord_members = numerize.numerize(int(dao['discordData']['totalMembers']))
        market_cap = token['financialData']['price'] * token['financialData']['totalSupply']
        market_cap = '$' + numerize.numerize(int(market_cap))
        logo = requests.get(dao['image'])
        logo = Image.open(BytesIO(logo.content))
        logo = logo.resize((200,200))
        base.paste(logo, (250, 550))
        title_font = ImageFont.truetype('/System/Library/Fonts/Keyboard.ttf', 90)
        sub_font = ImageFont.truetype('/System/Library/Fonts/Keyboard.ttf', 80)
        small_font = ImageFont.truetype('/System/Library/Fonts/Keyboard.ttf', 40)
        image_editable = ImageDraw.Draw(base)
        image_editable.text((250,800), name, (0, 0, 0), font=title_font)
        if positive == 1:
            image_editable.text((1280,670), f'{percent_change_7d:,.2f}%', (34, 139, 34), font=sub_font)
        else:
            image_editable.text((1280,670), f'{percent_change_7d:,.2f}%', (210, 43, 43), font=sub_font)
        image_editable.text((1280,880), market_cap, (0, 0, 0), font=sub_font)
        image_editable.text((1280,1090), discord_members, (0, 0, 0), font=sub_font)
        start = 950
        lines = textwrap.wrap(description, width=40)
        for d in lines:
            image_editable.text((250, start), d, (0,0,0), font=small_font)
            start += 60
        base.save("result.png")
    else:
        create_image()

if __name__ == '__main__':
    create_image()