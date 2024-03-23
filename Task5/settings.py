import json

FILE_PATH = 'settings.json'


def create_file():
    settings_dict = {'game_w': 15, 'game_h': 15}
    f = open(FILE_PATH, 'w')
    f.write(json.dumps(settings_dict))
    f.close()


def read_file():
    try:
        with open(FILE_PATH, 'r') as f:
            settings_dict = json.loads(f.read())
            return settings_dict
    except:
        create_file()
        return read_file()


def get_parameter(key):
    settings_dict = read_file()
    return settings_dict.get(key)


def set_parameter(key, value):
    settings_dict = dict(read_file())
    settings_dict.update({key: value})
    f = open(FILE_PATH, 'w')
    f.write(json.dumps(settings_dict))
    f.close()
