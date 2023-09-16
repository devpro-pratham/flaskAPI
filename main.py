from flask import Flask, request
import pymongo
import json
import re

with open('config.json') as config_file:
    params = json.load(config_file)["params"]

app = Flask(__name__)

client = pymongo.MongoClient(params["client_url"])
db = client[params["db"]]
# declare the dict to store the data
data = {}
@app.route("/")
def home():
    # display text on home page
    return "<h1>Webhook is Working!</h1>"

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    req = request.get_json(silent=True, force=True)
    query = req["queryResult"]["queryText"]
    result = req["queryResult"]["fulfillmentText"]
    # save the data in dictionary
    if(result == "What is your Last Name?"):
        data["fname"] = query
        print(data)

    if(result.__contains__("What is your email ID?")):
        # add the last name to the dictionary
        data["lname"] = query
        print(data)

    if(result.__contains__("What is your Phone Number?")):
        # use regex to extract the email id
        email = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", query)
        # add the email id to the dictionary
        data["email"] = email[0]
        print(data)

    if(result.__contains__("Thank You For Your Details")):
        # use regex to extract the phone number
        phone = re.findall(r"^[2-9]\d{2}-\d{3}-\d{4}$|^(1?(-?\d{3})-?)?(\d{3})(-?\d{4})$", query)
        # add the phone number to the dictionary
        data["phone"] = phone[0]
        print(data)

    # check if fname, lname, email, phone are present in the dictionary
    if("fname" in data and "lname" in data and "email" in data and "phone" in data):
        # insert the data in the database
        db.data.insert_one(data)
        print("Data inserted successfully")

    return {"fulfillmentText": result}, print(data)


if __name__ == "__main__":
    app.run()