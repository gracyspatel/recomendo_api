# Dependencies
from flask import Flask, request, jsonify
import traceback
import joblib

import pandas as pd
import numpy as np

from collections import defaultdict



app =  Flask(__name__)

@app.route("/")
def hello():
    return("WELCOME TO THE FILTERING SYSTEM APIS")


# API endpint /songs
@app.route('/songs', methods=['POST'])
def predict_songs():
        try:
            content_type = request.headers.get('Content-Type')
            if (content_type == 'application/json'):
                json = request.json
            song_name = json['song']

            data = joblib.load("./Pickle/Songs/model_songdata.pkl")

            # pred = recommend_songs([{'name': song_name, 'year':2020}],  data,20)
            return jsonify({"song_name": "song_name"},{"prediction": "pred"})

        except:

            return jsonify({'trace': traceback.format_exc()})

