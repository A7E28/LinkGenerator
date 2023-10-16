
![Logo](https://github.com/A7E28/helper_funcs/assets/110674887/573067ed-a1fb-4d2a-a103-114d0f8dd192)


# Link Generator

A Simple BOT for telegram  private groups based on python. It can generate invite links based on x number of user for x time. 

## Features

- Generates Invite Links.
- Revoke Links
- Migrateid
  



## Migrateid
This cmd needs an userid to work. The bot will ban the user who issued the command and send an invite link to the new user for that group, which is valid for 1 user for 5 min.
This is useful when someone wants to migrate their id. They don't have to ask the admin for another invite link.
## Deployment

To deploy this bot you need to install lib from requirements file. Open your shell and run 





```bash
  pip install -r requirements.txt 
```

Open the .env file and replace token_here with actual token of your bot.

Now you are ready to run the bot.
```bash
  python3 LinkGenerator.py 
```



## How to use the exe file of this bot?
If you want to use the exe file its pretty easy to use. Just download the latest release and edit the .env file add your token, run the exe file and you are done.
## Support

Join our [telegram group](https://t.me/TheHypernovaSupport)
 for any kind of Support.

