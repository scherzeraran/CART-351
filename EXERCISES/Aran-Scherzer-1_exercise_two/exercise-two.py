# ==========================================================
# CART 351 - EXERCISE TWO
# Flask + Jinja templates + NASA Images API (GET requests)
# ==========================================================

# 1. Imports
from flask import Flask, render_template, request, redirect, url_for
import requests

# 2. Create Flask app
app = Flask(__name__)

# 3. Base address of the NASA Image API search endpoint
NASA_SEARCH_URL = "https://images-api.nasa.gov/search"


# 4. The default route
@app.route("/")
def index():
    return render_template("index.html")


# *************************************************
# Task-1: GET REQUEST
# *************************************************
# 5. Page with the search form (no results yet)
@app.route("/t1")
def t1():
    return render_template("t1.html", have_results=False)


# 6. Receives the form data (GET) and asks NASA for ONE image
@app.route("/getSearchCriteria")
def getSearchCriteria():
    # 6.1 Get the text the user typed (sent as ?search_term=...)
    user_input = request.args.get("search_term", "").strip()

    # 6.2 If nothing typed, shows empty page again
    if user_input == "":
        return render_template("t1.html", have_results=False)

    # 6.3 Build the URL: base url + q=<user input> + media_type=image
    url = NASA_SEARCH_URL
    parameters = {"q": user_input, "media_type": "image"}

    # 6.4 Perform the API request
    response = requests.get(url, params=parameters, timeout=15)

    # 6.5 Convert the JSON answer into a Python dictionary
    data = response.json()

    # 6.6 The results are a list at data['collection']['items']
    items = data["collection"]["items"]

    # 6.7 No matches for this search: show the empty page again
    if len(items) == 0:
        return render_template("t1.html", have_results=False)

    # 6.8 First element of the list
    first_item = items[0]

    # 6.9 First image href from the "links" key
    imgFromNasa = first_item["links"][0]["href"]

    # 6.10 First description from the "data" key
    description = first_item["data"][0]["description"]

    # 6.11 Replaces the empty spaces so url is encoded
    imgFromNasa = imgFromNasa.replace(' ', '%20')

    # 6.12 Sends everything to the template
    return render_template("t1.html",
                           have_results=True,
                           description=description,
                           imgPath=imgFromNasa
                           )


# *************************************************
# Task-2: GET REQUEST
# *************************************************
# 7. Page with the search form
@app.route("/t2")
def t2():
    return render_template("t2.html")


# 8. Receives the form data (GET) and asks NASA for ALL the images
@app.route("/getSearchCriteria_adv")
def getSearchCriteria_adv():
    # 8.1 Get the text the user typed
    user_input = request.args.get("search_term", "").strip()

    # 8.2 The list sent to the template
    encodedImageLinks = []

    # 8.3 Only ask NASA if the user typed something
    if user_input != "":
        # 8.4 Same request as Task-1: q=<user input> and media_type=image
        url = NASA_SEARCH_URL
        parameters = {"q": user_input, "media_type": "image"}
        response = requests.get(url, params=parameters, timeout=15)

        # 8.5 JSON -> dictionary, then get the list of results
        data = response.json()
        items = data["collection"]["items"]

        # 8.6 Go through every result in the list
        for item in items:
            # 8.7 First image href from this item's "links" key
            singleImage = item["links"][0]["href"]

            # 8.8 Replace the spaces and add to the list
            encodedImageLinks.append(singleImage.replace(' ', '%20'))

    # 8.9 Send the list to the template
    return render_template("t2.html", images=encodedImageLinks)


# *************************************************
# 9. Run the development server
app.run(debug=True)
