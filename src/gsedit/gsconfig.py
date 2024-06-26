import json
import os

base_path = os.path.dirname(__file__)
config_path = os.path.join(base_path, 'gsconfig.json')

def get_config(name):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)

        return config[name]
    except FileNotFoundError:
        print("Config file not found, please ensure the config_path is correct and points to a proper config json.")
        return None

def change_config(name, change):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)

        config[name] = change

        with open(config_path, 'w') as file:
            json.dump(config, file)
    except FileNotFoundError:
        print("Config file not found, please ensure the config_path is correct and points to a proper config json.")
        return None
    
def get_color(name):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)

        return config["colors"][name]
    
    except FileNotFoundError:
        print("Config file not found, please ensure the config_path is correct and points to a proper config json.")
        return None

def get_consideration(name):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)

        return config["language-considerations"][name]

    except FileNotFoundError:
        print("Config file not found, please ensure the config_path is correct and points to a proper config json.")
        return None
    
def get_preference(category, pref):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)

        return config[category][pref]
    except FileNotFoundError:
        print("Config file not found, please ensure the config_path is correct and points to a proper config json.")
        return None

def get_layout(layout):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)

        return config["layouts"][layout]
    except FileNotFoundError:
        print("Config file not found, please ensure the config_path is correct and points to a proper config json.")
        return None
