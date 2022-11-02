# Dependencies
from flask import Flask
app =  Flask(__name__)

@app.route("/")
def hello():
    return("WELCOME TO THE FILTERING SYSTEM APIS")
