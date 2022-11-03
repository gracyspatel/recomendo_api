# Dependencies
from flask import Flask, request, jsonify
import traceback
import joblib

import pandas as pd
import numpy as np

from collections import defaultdict


def recommend_book(book_name):
    pt = joblib.load("./Pickle/Books/model_pt.pkl")
    similarity_score = joblib.load("./Pickle/Books/model_simscore.pkl")
    index = np.where(pt.index==book_name)[0][0]
    similar_items = sorted(list(enumerate(similarity_score[index])),key= lambda x:x[1],reverse = True)[1:11]
    booklist = []
    for i in similar_items:
        booklist.append(pt.index[i[0]])
    return booklist



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


# API endpint /movie to predict movies based on credits and keywords and genres
@app.route('/book', methods=['POST'])
def predict_book():
        try:
            content_type = request.headers.get('Content-Type')
            if (content_type == 'application/json'):
                json = request.json
            book_name = json['book']
            return jsonify({"book_name": book_name},{"recommendation":recommend_book(book_name)})

        except:

            return jsonify({'trace': traceback.format_exc()})

# API endpint /movie to predict movies based on credits and keywords and genres
@app.route('/topbook', methods=['GET'])
def top_book():
        try:
            topbooks = joblib.load("./Pickle/Books/model_topbooks.pkl")
            return topbooks.to_json(orient='table')

        except:

            return jsonify({'trace': traceback.format_exc()})
