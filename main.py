# Start scraping ...
import requests
from bs4 import BeautifulSoup
import csv
import json


BASE_URL = "https://www.prydwen.gg/page-data/star-rail/"
CHARACTERS_URL = BASE_URL + "characters/page-data.json"
LIGHTCONES_URL = BASE_URL + "light-cones/page-data.json"


def get_character_info(character_name):
    response = requests.get(BASE_URL + "characters/" + character_name + "/page-data.json")
    data = response.json()
    character = data["result"]["data"]["currentUnit"]["nodes"][0]
    # print(character)
    #      store in ./characters/character_name.json
    with open("./characters/" + character_name + ".json", "w") as file:
        # formatted json output
        json.dump(character, file, indent=4)


def get_characters_name():
    response = requests.get(CHARACTERS_URL)
    data = response.json()
    characters = data["result"]["data"]["allCharacters"]["nodes"]
    for character in characters:
        get_character_info(character["slug"])


def get_lightcones():
    response = requests.get(LIGHTCONES_URL)
    data = response.json()
    lightcones = data["result"]["data"]["allCharacters"]["nodes"]
    for lightcone in lightcones:
        get_lightcone_info(lightcone)

def get_lightcone_info(lightcone):
    with open("./light-cones/" + lightcone["slug"] + ".json", "w") as file:
        json.dump(lightcone, file, indent=4)

get_lightcones()