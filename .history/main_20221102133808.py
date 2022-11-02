# Dependencies
from flask import Flask, request, jsonify
import joblib
import traceback
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from collections import defaultdict
import numpy as np
# from scipy.spatial.distance import cdist

# sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id='2f829542ff1f4e84b19fbeed1564040e', client_secret='de618579836c40eabd682d8983d3fe3e'))

sp = joblib.load("./Pickle/Songs/model_sp.pkl")

number_cols = joblib.load("./Pickle/Songs/model_no_cols.pkl")

app =  Flask(__name__)

def get_song_data(song, spotify_data):
    
    try:
        song_data = spotify_data[(spotify_data['name'] == song['name']) 
                                & (spotify_data['year'] == song['year'])].iloc[0]
        return song_data
    
    except IndexError:
        return find_song(song['name'], song['year'])

def find_song(name, year):
    song_data = defaultdict()
    results = sp.search(q= 'track: {} year: {}'.format(name,year), limit=1)
    if results['tracks']['items'] == []:
        return None

    results = results['tracks']['items'][0]
    track_id = results['id']
    audio_features = sp.audio_features(track_id)[0]

    song_data['name'] = [name]
    song_data['year'] = [year]
    song_data['explicit'] = [int(results['explicit'])]
    song_data['duration_ms'] = [results['duration_ms']]
    song_data['popularity'] = [results['popularity']]

    for key, value in audio_features.items():
        song_data[key] = value

    return pd.DataFrame(song_data)

def get_mean_vector(song_list, spotify_data):
    
    song_vectors = []
    
    for song in song_list:
        song_data = get_song_data(song, spotify_data)
        if song_data is None:
            print('Warning: {} does not exist in Spotify or in database'.format(song['name']))
            continue
        song_vector = song_data[number_cols].values
        song_vectors.append(song_vector)  
    
    song_matrix = np.array(list(song_vectors))
    return np.mean(song_matrix, axis=0)

def flatten_dict_list(dict_list):
    
    flattened_dict = defaultdict()
    for key in dict_list[0].keys():
        flattened_dict[key] = []
    
    for dictionary in dict_list:
        for key, value in dictionary.items():
            flattened_dict[key].append(value)
            
    return flattened_dict

def recommend_songs( song_list, spotify_data, n_songs=10):
    
    metadata_cols = ['name', 'year', 'artists']
    song_dict = flatten_dict_list(song_list)
    song_center = get_mean_vector(song_list, spotify_data)
    song_cluster_pipeline = joblib.load("./Pickle/Songs/model_cluster_pipeline.pkl")
    scaler = song_cluster_pipeline.steps[0][1]
    scaled_data = scaler.transform(spotify_data[number_cols])
    scaled_song_center = scaler.transform(song_center.reshape(1, -1))
    
    cdist = joblib.load("./Pickle/Songs/model_cdist.pkl")

    distances = cdist(scaled_song_center, scaled_data, 'cosine')
    index = list(np.argsort(distances)[:, :n_songs][0])
    
    rec_songs = spotify_data.iloc[index]
    rec_songs = rec_songs[~rec_songs['name'].isin(song_dict['name'])]
    return rec_songs[metadata_cols].to_dict(orient='records')


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

            pred = recommend_songs([{'name': song_name, 'year':2020}],  data,20)
            return jsonify({"song_name": song_name},{"prediction": pred})

        except:

            return jsonify({'trace': traceback.format_exc()})

