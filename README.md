**About**

This bot is focused on economic od a server. User can show all available commands, his own balance, send money to other user. If a user is administrator he can also check other user's balance, increase or decrease their balance and change starting amount of money for new members. Commands and messages of the bot are in Czech language.

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

**How to run**

1. python3 -m venv env
2. source env/bin/activate
3. pip3 install -r requirements.txt
4. python3 bot.py