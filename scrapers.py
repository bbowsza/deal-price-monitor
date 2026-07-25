import requests
import re

from bs4 import BeautifulSoup



HEADERS = {
    "User-Agent":
    "Mozilla/5.0"
}



def get_page(url):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=60
        )

        if response.status_code != 200:
            return None

        return response.text


    except Exception as e:

        print(
            "Request error:",
            e
        )

        return None





def check_terms(text, product):

    text = text.lower()


    for term in product["required_terms"]:

        if term.lower() not in text:
            return False



    for term in product["excluded_terms"]:

        if term.lower() in text:
            return False


    return True






def check_stock(text):

    bad_terms = [

        "out of stock",
        "sold out",
        "currently unavailable",
        "temporarily unavailable"

    ]


    text=text.lower()


    for term in bad_terms:

        if term in text:
            return False


    return True





def extract_prices(text):

    prices = re.findall(
        r"\$(\d{1,4}(?:\.\d{2})?)",
        text
    )


    results=[]


    for price in prices:

        try:

            value=float(price)


            if value >= 20:
                results.append(value)


        except:

            pass



    return results





def extract_links(soup):

    links=[]


    for a in soup.find_all(
        "a",
        href=True
    ):

        href=a["href"]


        if href.startswith("/"):

            continue


        if href.startswith("http"):

            links.append(href)



    return links





def shopify_price(url, product):

    try:

        response=requests.get(
            url,
            headers=HEADERS,
            timeout=60
        )


        data=response.json()


        title = data.get(
            "title",
            ""
        ).lower()


        if not check_terms(
            title,
            product
        ):
            return None



        prices=[]


        for variant in data.get(
            "variants",
            []
        ):

            if variant.get("price"):

                prices.append(
                    float(
                        variant["price"]
                    )
                    /
                    100
                )


        if prices:

            return {

                "price":min(prices),

                "url":url

            }


    except Exception as e:

        print(
            "Shopify error:",
            e
        )


    return None
        ):


            if variant.get("price"):

                prices.append(
                    float(
                        variant["price"]
                    )
                    /
                    100
                )



        if prices:

            return {

                "price":min(prices),

                "url":url

            }


    except Exception as e:

        print(
            "Shopify error:",
            e
        )


    return None





def search_page(url, product):


    html=get_page(url)


    if not html:

        return None



    soup=BeautifulSoup(
        html,
        "lxml"
    )


    text=soup.get_text(
        " ",
        strip=True
    )



    if not check_terms(
        text,
        product
    ):

        return None



    if not check_stock(
        text
    ):

        return None



    prices=extract_prices(
        text
    )



    valid=[]


    for price in prices:


        if price <= product["target_price"] * 1.5:

            valid.append(price)



    if not valid:

        return None



    links=extract_links(
        soup
    )


    return {

        "price":min(valid),

        "url":
        links[0] if links else url

    }
