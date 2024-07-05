import os
import json


def get_theme_data():
    base_path = os.path.dirname(__file__)
    theme_file_path = os.path.join(base_path, 'active-editor-theme.json')
    with open(theme_file_path, 'r') as file:
        theme_data = json.load(file)
    return theme_data

def replace_qss():
    theme_data = get_theme_data()
    main_color = theme_data['active-theme']['colors']['main_color']
    secondary_color = theme_data['active-theme']['colors']['secondary_color']
    font_color = theme_data['active-theme']['colors']['font_color']
    base_path = os.path.dirname(__file__)
    original_directory = os.path.join(base_path, 'original-css')
    os.makedirs(original_directory, exist_ok=True)
    css_dir = os.path.join(base_path, 'css')

    for filename in os.listdir(original_directory):
        src = os.path.join(original_directory, filename)
        dest = os.path.join(css_dir, filename)
        if os.path.isfile(src):
            with open(src, 'r') as f, open(dest, 'w') as d:
                d.write(f.read())

    for filename in os.listdir(css_dir):
        src = os.path.join(css_dir, filename)
        dest = os.path.join(original_directory, filename)
        if os.path.isfile(src):
            with open(src, 'r') as f, open(dest, 'w') as d:
                d.write(f.read())
            
    for filename in os.listdir(css_dir):
        if filename.endswith('.qss'):
            filepath = os.path.join(css_dir, filename)
            with open(filepath, 'r') as file:
                content = file.read()

            content = content.replace('"@main_color"', main_color)
            content = content.replace('"@secondary_color"', secondary_color)
            content = content.replace('"@font_color"', font_color)

            with open(filepath, 'w') as file:
                file.write(content)
