import os
import json
import smtplib

from datetime import datetime, timezone
from email.message import EmailMessage

from sources import SOURCES
from scrapers import shopify_price, search_page


PRODUCT_FILE = "products.json"
STATE_FILE = "state.json"


with open(PRODUCT_FILE) as f:
    PRODUCTS = json.load(f)



def load_state():

    try:

        with open(STATE_FILE) as f:
            return json.load(f)

    except:

        return {}



def save_state(data):

    with open(STATE_FILE, "w") as f:

        json.dump(
            data,
            f,
            indent=2
        )



def send_email(product, deal):

    sender = os.environ["EMAIL_FROM"]
    password = os.environ["EMAIL_PASSWORD"]
    recipient = os.environ["EMAIL_TO"]


    msg = EmailMessage()


    msg["Subject"] = (
        f"🚨 {product['name']} ${deal['price']:.2f}"
    )


    msg["From"] = sender
    msg["To"] = recipient


    msg.set_content(
f"""
DEAL FOUND

Product:
{product['name']}

Price:
${deal['price']:.2f}

Store:
{deal['store']}

Link:
{deal['url']}

Target:
${product['target_price']}

Time:
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

        smtp.send_message(msg)



state = load_state()


print("Starting monitor")



for product in PRODUCTS:

    print(
        "\nChecking:",
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
                or result["price"] < best["price"]
            ):

                best = result
    if best:

        print(
            "Best deal:",
            best
        )


        alert_key = (
            product["name"]
            +
            str(best["price"])
        )


        if (
            best["price"] <= product["target_price"]
            and alert_key not in state
        ):

            send_email(
                product,
                best
            )


            state[alert_key] = True



save_state(state)


print("Finished")
