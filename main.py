import csv
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from config import CHANNEL_ACCESS_TOKEN, CHANNEL_SECRET, GROUP, MYSELF


api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


app = Flask(__name__)


# get messages from Line
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


# handle and receive messages from users
@handler.add(MessageEvent, message=TextMessage)
def handle(event):
    in_group = hasattr(event.source, "group_id") and str(event.source.group_id) == GROUP
    myself = str(event.source.user_id) == MYSELF

    if not myself and not in_group:
        print("Incident: not myself and not in group")
        print(event.source.user_id)
        print("------------")
        return

    if myself and not in_group:
        print("Incident: myself and not in group (testing)")
        print("------------")

    msg = event.message.text
    tok = event.reply_token

    if msg[0] == "/":
        if msg.split()[0] == "/add" and all(
            char.isnumeric() for char in msg.split()[-1]
        ):
            # the last place in the command is a number
            reply_text = add(
                " ".join(msg.split()[1:]),
                myself and not in_group,
            )
            api.reply_message(
                tok,
                TextSendMessage(text=reply_text),
            )
        elif msg.split()[0] == "/summary":
            reply_text = summary(msg.split()[1])
            api.reply_message(
                tok,
                TextSendMessage(text=reply_text),
            )
        elif msg.split()[0] == "/list":
            reply_text = (
                list_entries(msg.split()[1:])
                if msg.rstrip().count(" ")
                else list_entries("")
            )
            api.reply_message(
                tok,
                TextSendMessage(text=reply_text),
            )
        elif msg == "/usage":
            reply_text = usage()
            api.reply_message(
                tok,
                TextSendMessage(text=reply_text),
            )
        else:
            api.reply_message(
                tok,
                TextSendMessage(
                    text="I don't understand what you're trying to say.\nType \"/usage\" to see more info."
                ),
            )


def add(msg, testing):
    """
    possible commands:
    - /add A B 100
    - /add A B -100
    """

    debtor = msg.split()[0]
    creditor = msg.split()[1]
    amount = msg.split()[2]

    try:
        with open(
            file="record.csv",
            encoding="utf-8",
            mode="a",
            newline="",
        ) as f:
            new_entry = [debtor, creditor, amount, testing]

            writer = csv.writer(f)
            writer.writerow(new_entry)
            return "Entry added successfully"

    except Exception as e:
        return "An error occurred: \n" + str(e)


def summary(msg):
    """
    possible commands:
    - /summary A
    """

    d = dict()
    name = msg

    try:
        with open(
            file="record.csv",
            encoding="utf-8",
            mode="r",
        ) as f:
            reader = csv.reader(f)
            for row in reader:
                # if it's not testing
                if row[3] == str(False):
                    if row[0] == name:
                        # owes money
                        if d.get(row[1]) == None:
                            d[row[1]] = int(row[2])
                        else:
                            d[row[1]] += int(row[2])
                    elif row[1] == name:
                        # is owed money
                        if d.get(row[0]) == None:
                            d[row[0]] = -int(row[2])
                        else:
                            d[row[0]] -= int(row[2])

        return (
            "總共欠:\n------------\n"
            + "\n".join([f"{key.ljust(4)} {val}塊錢" for key, val in d.items()])
            if d != {}
            else "沒有欠錢"
        )

    except Exception as e:
        return "An error occurred: \n" + str(e)


def list_entries(msg):
    """
    possible commands:
    - /list
    - /list A
    - /list all
    - /list A all
    """

    l = list()
    name = ""
    testing = False
    if msg != "":
        name = msg[0] if msg[0] != "all" else ""
        testing = (
            True if (len(msg) > 1 and msg[1] == "all") or msg[0] == "all" else False
        )

    try:
        with open(
            file="record.csv",
            encoding="utf-8",
            mode="r",
        ) as f:
            reader = csv.reader(f)
            for row in reader:
                if testing:
                    if name != "" and row[0] == name or row[1] == name or name == "":
                        l.append(row)
                else:
                    if row[3] == str(False):
                        if (
                            name != ""
                            and row[0] == name
                            or row[1] == name
                            or name == ""
                        ):
                            l.append(row[:-1])

    except Exception as e:
        return "An error occurred: \n" + str(e)

    reply_text = (
        (
            f"list of {'all' if testing else ''} entries including {name}:\n------------\n"
            if name != ""
            else f"list of {'all' if testing else ''} entries:\n------------\n"
        )
        + "\n".join(
            [
                f"{row[0].ljust(4)} {row[1].ljust(4)} {row[2].ljust(4)} {row[3] if testing else ''}"
                for row in l
            ]
        )
        if l != []
        else "no entries found"
    )

    return reply_text


def usage():
    msg = """
    usage:
    ------------
    /add <debtor> <creditor> <amount>
    - to add a new entry to the record
    - <debtor> and <creditor> are names (strings)
    - <amount> is a number (either positive or negative)
    - example: /add A B 100
    ------------
    /summary <name>
    - to get the summary of a person
    - <name> is a string
    - example: /summary A all
    ------------
    /list <name> all
    - to get the list of entries from records
    - <name> is a string (optional)
    - "all" is a keyword (string, optional), to show testing entries as well
    - example: /list A all
    ------------
    /usage
    - to see this message again

    
    !!!DISCLAIMER!!!
    - only me in the private chat and requests from this group will this bot respond to
    - entries added by myself in the private chat will be marked as "testing"
    """

    return msg


if __name__ == "__main__":
    app.run()
