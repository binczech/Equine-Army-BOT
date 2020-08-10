import os
from dotenv import load_dotenv


load_dotenv()


class Config:

    extensions = ['economics', 'rewards', 'roles']
    TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD = os.getenv('DISCORD_GUILD')
    MONGODB_URI = os.getenv('MONGODB_URI')
    DB_NAME = os.getenv('DB_NAME')
    LOG_CHANNEL = os.getenv('LOG_CHANNEL')
    WELCOME_CHANNEL = os.getenv('WELCOME_CHANNEL')
    ROLES_CHANNEL = os.getenv('ROLES_CHANNEL')  # TODO
    REWARDS_CHANNEL = os.getenv('REWARDS_CHANNEL')
