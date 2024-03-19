import json


def load_config_from_json(app, json_file):
    with open(json_file) as file:
        config = json.load(file)
        app.config.from_mapping(config)


