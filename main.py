# Start scraping ...
import requests
from bs4 import BeautifulSoup
import csv
import json
import os
import pandas as pd

BASE_URL = "https://www.prydwen.gg/page-data/star-rail/"
CHARACTERS_URL = BASE_URL + "characters/page-data.json"
LIGHTCONES_URL = BASE_URL + "light-cones/page-data.json"
RELICS_URL = "https://www.prydwen.gg/page-data/star-rail/guides/relic-sets/page-data.json"


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


def get_relic_info(relic):
    relic_name = relic["name"].lower().replace(":", "").replace(" ", "-")
    with open("./relics/" + relic_name + ".json", "w") as file:
        json.dump(relic, file, indent=4)


def get_relics():
    response = requests.get(RELICS_URL)
    data = response.json()
    relics = data["result"]["data"]["allCharacters"]["nodes"]
    for relic in relics:
        get_relic_info(relic)


def raw_to_formatted(raw):
    data = json.loads(raw)

    def traverse(node):
        text = ''
        if isinstance(node, dict):
            if 'value' in node:
                text += node['value']
            if 'content' in node:
                for item in node['content']:
                    text += traverse(item)
        elif isinstance(node, list):
            for item in node:
                text += traverse(item)
        return text

    return traverse(data)


def format_json(data):

    if isinstance(data, dict):
        keys = list(data.keys())
        if "raw" in keys:
            data["formatted"] = raw_to_formatted(data["raw"])
            data.pop("raw", None)
        for key in keys:
            if isinstance(data.get(key), dict):
                format_json(data[key])
            elif isinstance(data.get(key), list):
                for item in data[key]:
                    format_json(item)



def format_json_files():
    folders = ["characters", "light-cones", "relics"]
    for folder in folders:
        for file in os.listdir("./" + folder):
            path = "./" + folder + "/" + file
            output = ""
            with open(path, "r") as jsonFile:
                data = json.load(jsonFile)
                data.pop("id", None)
                data.pop("updatedAt", None)
                data.pop("createdAt", None)
                format_json(data)
                output = data
            new_path = "./formatted/" + folder + "/" + file
            with open(new_path, "w") as jsonFile:
                json.dump(output, jsonFile, indent=4)


format_json_files()
