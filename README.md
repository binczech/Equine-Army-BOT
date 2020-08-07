**About**

This bot is focused on economic of a server. User can show all available commands, his own balance, send money to other user. If a user is administrator he can also check other user's balance, increase or decrease their balance and change starting amount of money for new members. Commands and messages of the bot are in Czech language.

Uses MongoDB for storing of values. Expected syntax of DB is:
```
{
    "start-money": 5000,
    "users": 
    {
        "user#1234": 6000,
        "user#6789": 5000
    }
}
```

Enviromental variables that are needed to be filled into `.env` file:
* DISCORD_TOKEN - Token for Discord bot from Discord Developer Portal
* DISCORD_GUILD - Name of Discord server
* MONGODB_URI - MongoDB URI for connection to MongoDB
* DB_NAME - Database name
* LOG_CHANNEL - Channel for logging
* WELCOME_CHANNEL - Channel for welcoming users
* ROLES_CHANNEL - Channel for adding roles (TODO)
* REWARDS_CHANNEL - Channel for setting rewards

**Commands**

*User Commands:*  
!příkazy - Shows list of available commands.  
!peníze - Shows current balance of a user who sent the command.  
!platba @user amount - Sends an amount of money to other user.  
*Administrator Commands:*  
!kontrola @user - Shows balance of a user  
!připsat-start amount - Changes starting amount of money for new users  
!připsat @user amount - Adds amount of money to a user  
!odebrat @user amount - Removes amount of money to a user  

**Reactions**

*Admin Reactions:*
* When admin adds to a message one reaction mentioned and valued in REWARDS_CHANNEL, money will be awarded to author of the message.
* When admin removes the reaction, money will be taken back.

**Channels**

*Rewards Channel:*
* Must contain lines in messages in this format: \[emote\]\[2 spaces\]\[number of money\]\[2 spaces\]\[description of reward\]

**Extensions**

Extensions in terms of `discord.ext.commands.Cog` can be added. It is needed to add a `Cog` in a python file to the `extensions` folder and add name of the python file to `extensions` array in `config\config.py`.

**Prerequisities**

* python => 3.6
* python3-pip (sudo apt-get install python3-pip)
* virtualenv (sudo pip3 install virtualenv)

**How to run**

1. python3 -m venv env
2. source env/bin/activate
3. pip3 install -r requirements.txt
4. python3 bot.py