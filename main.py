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


def merge_files():
    folders = ["characters", "light-cones", "relics"]
    for folder in folders:
        merged = []
        for file in os.listdir("./formatted/" + folder):
            path = "./formatted/" + folder + "/" + file
            with open(path, "r") as jsonFile:
                data = json.load(jsonFile)
                merged.append(data)
        with open("./merged/" + folder + ".json", "w") as jsonFile:
            json.dump(merged, jsonFile, indent=4)

# "smallImage": {
#     "localFile": {
#         "childImageSharp": {
#             "gatsbyImageData": {
#                 "layout": "constrained",
#                 "backgroundColor": "#080808",
#                 "images": {
#                     "fallback": {
#                         "src": "/static/9c7de7c12904b5458ab5181b264bb33d/bf8e1/1_sm.png",
#                         "srcSet": "/static/9c7de7c12904b5458ab5181b264bb33d/914ee/1_sm.png 32w,\n/static/9c7de7c12904b5458ab5181b264bb33d/1c9ce/1_sm.png 64w,\n/static/9c7de7c12904b5458ab5181b264bb33d/bf8e1/1_sm.png 128w",
#                         "sizes": "(min-width: 128px) 128px, 100vw"
#                     },
#                     "sources": [
#                         {
#                             "srcSet": "/static/9c7de7c12904b5458ab5181b264bb33d/ef6ff/1_sm.webp 32w,\n/static/9c7de7c12904b5458ab5181b264bb33d/8257c/1_sm.webp 64w,\n/static/9c7de7c12904b5458ab5181b264bb33d/6766a/1_sm.webp 128w",
#                             "type": "image/webp",
#                             "sizes": "(min-width: 128px) 128px, 100vw"
#                         }
#                     ]
#                 },
#                 "width": 128,
#                 "height": 128
#             }
#         }
#     }
# },

# extact images and put them in the following format
#{  "images": 
    # {
    #   "src": [ https://www.prydwen.gg/static/9c7de7c12904b5458ab5181b264bb33d/ef6ff/1_sm.webp, https://www.prydwen.gg/static/9c7de7c12904b5458ab5181b264bb33d/8257c/1_sm.webp, https://www.prydwen.gg/static/9c7de7c12904b5458ab5181b264bb33d/6766a/1_sm.webp],
    #   "type": "image/webp",
    # }
# }

def extract_images_light_cones():
    with open("./merged/light-cones.json", "r") as jsonFile:
        data = json.load(jsonFile)
        for light_cone in data:
            if "smallImage" in light_cone:
                image = light_cone["smallImage"]["localFile"]["childImageSharp"]["gatsbyImageData"]["images"]["fallback"]["src"]
                image_url = "https://www.prydwen.gg" + image
                light_cone["image"] = image_url
                light_cone.pop("smallImage", None)
    with open("./merged/light-cones.json", "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)


def extract_images_relics():
    with open("./merged/relics.json", "r") as jsonFile:
        data = json.load(jsonFile)
        for relic in data:
            if "image" in relic:
                image = relic["image"]["localFile"]["childImageSharp"]["gatsbyImageData"]["images"]["fallback"]["src"]
                image_url = "https://www.prydwen.gg" + image
                relic["image"] = image_url
    with open("./merged/relics.json", "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)

def extract_images_characters():
    with open("./merged/characters.json", "r") as jsonFile:
        data = json.load(jsonFile)
        for character in data:
            if "smallImage" in character:
                try:
                    image = character["smallImage"]["localFile"]["childImageSharp"]["gatsbyImageData"]["images"]["fallback"]["src"]
                    image_url = "https://www.prydwen.gg" + image
                    character["smallImage"] = image_url
                except:
                    character.pop("smallImage", None)
                    character["smallImage"] = ""
            if "cardImage" in character:
                try:
                    image = character["cardImage"]["localFile"]["childImageSharp"]["gatsbyImageData"]["images"]["fallback"]["src"]
                    image_url = "https://www.prydwen.gg" + image
                    character["cardImage"] = image_url
                except:
                    character.pop("cardImage", None)
                    character["cardImage"] = ""
            if "fullImage" in character:
                try:
                    image = character["fullImage"]["localFile"]["childImageSharp"]["gatsbyImageData"]["images"]["fallback"]["src"]
                    image_url = "https://www.prydwen.gg" + image
                    character["fullImage"] = image_url
                except:
                    character.pop("fullImage", None)
                    character["fullImage"] = ""
    with open("./merged/characters.json", "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)

extract_images_characters()