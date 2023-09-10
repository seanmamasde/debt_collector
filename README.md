# debt_collector

## A little self-made debt collector for Line group chat

**Setting Up**

-   Have a `config.py` file which contains your `CHANNEL_ACCESS_TOKEN`, `CHANNEL_SECRET`, `MYSELF` (your user id in Line) and `GROUP` (your group id in line) to begin with
-   Fire up ngrok server by running `ngrok http 5000`
-   Run `python ./main.py` to get the bot working
-   In your Line Dev Console, change the webhook url to whatever ngrok gives you and add `/callback` at the end, like: `https://d5d1-220-132-157-246.ngrok.io/callback`
-   You're good to go

**Side Note**

-   Ngrok server without an auth token WILL EXPIRE in around 2 hours, if you want to keep it running, make sure to register an account at [ngrok.com](https://ngrok.com/) and add the auth token beforehand
-   To figure out what your user id and group id is in Line, see [official documentation](https://developers.line.biz/en/reference/messaging-api/#source-group)
-   This project is based off [this article](https://ithelp.ithome.com.tw/articles/10229943) cus I am too lazy to figure it all out by myself from scratch. It could be a little bit outdated as of the time of coding (the article is already 3yrs old). Probably won't change anyways it if not necessary, since it's deprecated not unsupported, so just let it be
