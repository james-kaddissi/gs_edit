import json
import os

def read_theme_file():
    base_path = os.path.dirname(__file__)
    theme_file_path = os.path.join(base_path, 'active-theme.json')
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
