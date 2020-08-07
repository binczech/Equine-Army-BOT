import json
import pymongo
from config.config import Config


def open_json():
    with open('money.json') as json_file:
        data = json.load(json_file)
    return data


def save_json(data):
    with open('money.json', 'w') as outfile:
        json.dump(data, outfile)


def open_db():
    client = pymongo.MongoClient(Config.MONGODB_URI)
    db = client.get_default_database()
    money = db[Config.DB_NAME]
    return client, money


def read_db():
    client, money = open_db()
    data = money.find_one()
    client.close()
    return data


def save_db(data):
    client, money = open_db()
    money.replace_one({'_id': data['_id']}, data, upsert=True)
    client.close()


# user_id should be string
def change_users_money(user_id, value):
    data = read_db()
    if user_id in data['users'].keys():
        data['users'][user_id] += value
    else:
        start_value = data['start-money']
        data['users'][user_id] = start_value + value
    new_value = data['users'][user_id]
    save_db(data)
    return new_value


# user_id should be string
def get_user_money(user_id):
    data = read_db()
    if user_id in data['users'].keys():
        value = data['users'][user_id]
    else:
        start_value = data['start-money']
        data['users'][user_id] = start_value
        save_db(data)
    return value


def cut_string(string: str, part_len: int):
    return list(
        string[0+i:part_len+i] for i in range(0, len(string), part_len)
    )
