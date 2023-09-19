from flask import Flask, request
import pymongo
import json
import re

with open('config.json') as config_file:
    params = json.load(config_file)["params"]

app = Flask(__name__)

client = pymongo.MongoClient(params["client_url"])
db = client[params["db"]]
data = {}

@app.route("/")
def home():
    return "<h1>Webhook is Working!</h1>"

def addData():
    req = request.get_json(silent=True, force=True)
    query = req["queryResult"]["queryText"]
    action = req.get('queryResult').get('action')

    if(action == "input.fname"):
        data["fname"] = query
        print(data)

    if(action == "input.lname"):
        # add the last name to the dictionary
        data["lname"] = query
        print(data)

    if(action == "input.email"):
        # use regex to extract the email id
        if(re.search(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", query) == None):
            return {"fulfillmentText": "Please enter a valid email id"}
        email = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", query)
        # add the email id to the dictionary
        data["email"] = email[0]
        print(data)
    


    if(action == "input.phone"):
        # use regex to extract the phone number
        if(re.search(r"^[2-9]\d{2}-\d{3}-\d{4}$|^(1?(-?\d{3})-?)?(\d{3})(-?\d{4})$", query) == None):
            return {"fulfillmentText": "Please enter a valid phone number"}
        phone = re.findall(r"^[2-9]\d{2}-\d{3}-\d{4}$|^(1?(-?\d{3})-?)?(\d{3})(-?\d{4})$", query)
        # add the phone number to the dictionary
        data["phone"] = phone[0]
        

    # check if fname, lname, email, phone are present in the dictionary
    if("fname" in data and "lname" in data and "email" in data and "phone" in data):
        # insert the data in the database
        db.data.insert_one(data)
        print("Data inserted successfully")

    return 0

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    return addData()

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=81)
