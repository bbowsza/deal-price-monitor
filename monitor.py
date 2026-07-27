import os
import json
import smtplib

from datetime import datetime, timezone
from email.message import EmailMessage

from sources import SOURCES

from scrapers import (
    shopify_price,
    search_page
)


PRODUCT_FILE = "products.json"
STATE_FILE = "state.json"


# -----------------------------
# Load products
# -----------------------------

with open(PRODUCT_FILE) as f:
    PRODUCTS = json.load(f)


# -----------------------------
# State management
# -----------------------------

def load_state():

    try:
        with open(STATE_FILE) as f:
            return json.load(f)

    except:
        return {}



def save_state(data):

    with open(
        STATE_FILE,
        "w"
    ) as f:

        json.dump(
            data,
            f,
            indent=2
        )


# -----------------------------
# Email + SMS alert
# -----------------------------

def send_email(product, deal):

    sender = os.environ["EMAIL_FROM"]
    password = os.environ["EMAIL_PASSWORD"]

    recipients = [
        os.environ["EMAIL_TO"],
        os.environ["SMS_EMAIL"]
    ]


    msg = EmailMessage()


    msg["Subject"] = (
        f"🚨 Deal Alert: {product['name']} ${deal['price']:.2f}"
    )


    msg["From"] = sender

    msg["To"] = ", ".join(recipients)


    msg.set_content(
f"""
DEAL FOUND

Product:
{product['name']}

Price:
${deal['price']:.2f}

Target Price:
${product['target_price']:.2f}

Store:
{deal['store']}

Purchase Link:
{deal['url']}

Detected:
{datetime.now(timezone.utc)}

"""
    )


    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as smtp:

        smtp.login(
            sender,
            password
        )

        smtp.send_message(
            msg,
            from_addr=sender,
            to_addrs=recipients
        )


# -----------------------------
# Main monitor
# -----------------------------

print(
    "Starting monitor"
)


state = load_state()


for product in PRODUCTS:

    print()

    print(
        "Checking:",
        product["name"]
    )


    best = None


    for source in SOURCES:


        print(
            "Checking source:",
            source["name"]
        )


        url = source["url"].format(

            query=
            product["search_query"]
            .replace(
                " ",
                "+"
            )

        )


        result = None


        if source["type"] == "shopify":

            result = shopify_price(
                url,
                product
            )


        else:

            result = search_page(
                url,
                product
            )


        if result:

            result["store"] = source["name"]


            if (
                best is None
                or
                result["price"] < best["price"]
            ):

                best = result



    if best:


        print(
            "Best:",
            best
        )


        alert_key = (
            product["name"]
            +
            str(best["price"])
        )


        if (
            best["price"]
            <=
            product["target_price"]

            and

            alert_key not in state
        ):


            print(
                "Sending alert"
            )


            send_email(
                product,
                best
            )


            state[alert_key] = True



    else:

        print(
            "No deals found"
        )



save_state(
    state
)


print()

print(
    "Finished"
)
