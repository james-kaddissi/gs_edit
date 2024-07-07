import json
import os

def read_theme_file():
    base_path = os.path.dirname(__file__)
    theme_file_path = os.path.join(base_path, 'active-theme.json')
    with open(theme_file_path, 'r') as file:
        theme_data = json.load(file)
    return theme_data

def read_editor_theme_file():
    base_path = os.path.dirname(__file__)
    theme_file_path = os.path.join(base_path, 'active-editor-theme.json')
    with open(theme_file_path, 'r') as file:
        theme_data = json.load(file)
    return theme_data

def get_formatted_theme_array():
    arr = [] 
    data = read_theme_file()
    arr.append(data["active-theme"]["theme-name"])
    arr.append(data["active-theme"]["version"])

    syntax_rules = data["active-theme"]["syntax-rules"]
    
    def find_rule(rules, rule_name):
        for rule in rules:
            if rule_name in rule:
                return rule[rule_name]
        return None

    default_rule = find_rule(syntax_rules, "default")
    arr.append(default_rule["font-family"])

    for rule_name in ["default", "keyword", "types", "string", "keyargs", "brackets", "comments", "constants", "functions", "classes", "function_def"]:
        rule = find_rule(syntax_rules, rule_name)
        if rule:
            arr.append(rule["text-color"])
        else:
            arr.append(None)

    return arr

def write_theme_file(theme_data):
    base_path = os.path.dirname(__file__)
    theme_file_path = os.path.join(base_path, 'active-theme.json')
    with open(theme_file_path, 'w') as file:
        json.dump(theme_data, file, indent=4)

def write_editor_theme_file(theme_data):
    base_path = os.path.dirname(__file__)
    theme_file_path = os.path.join(base_path, 'active-editor-theme.json')
    with open(theme_file_path, 'w') as file:
        json.dump(theme_data, file, indent=4)

def write_active_theme(theme_data):
    active_theme = read_theme_file()
    active_theme["active-theme"] = theme_data
    write_theme_file(active_theme)
    
