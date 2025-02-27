from flask import Flask, jsonify, request, send_file
import pandas as pd
from glob import glob
from main import Main
from RandomForest import RandomForestModel
import time
import datetime
import pickle
from api_calls import ApiCall
import json
import urllib
import urllib.request
from urllib.parse import urlparse
import httplib2 as http  # external library

app = Flask(__name__)


@app.route("/live_image", methods=["GET"])
def return_live_image():
    camera_id = request.args.get('camera_id')
    for img_path in glob('./assets/*.jpg'):
        img_id = int(img_path.split("/")[-1].split("_")[0])
        if int(camera_id) == img_id:
            return send_file(img_path)

# to be updated when finalised


@app.route("/stats", methods=["GET"])
def get_stats():
    camera_id = request.args.get('camera_id')
    df = pd.read_csv('traffic_stats.csv')
    match_df = df.loc[df['Camera_Id'] == int(camera_id)]
    result_df = match_df[['Density', 'Average_Speed','Direction','Jam','Date','Time']]
    return jsonify(result_df.to_dict(orient="records"))

# for past data
# to update to GET if filtering is required


@app.route("/archive")
def return_past_data():
    df = pd.read_csv('traffic_stats.csv')
    return jsonify(df.to_dict(orient="records"))

# for prediction based on user input


@app.route("/prediction", methods=["GET"])
def make_prediction():
    time = request.args.get('time')
    date = request.args.get('date')
    camera_id = int(request.args.get('camera_id'))
    road = request.args.get('road')
    model = pickle.load(open("model.pkl", "rb"))
    result = model.predict(camera_id, road, date, time)
    if result == 0:
        return jsonify({'prediction': 'No Jam'})
    elif result == 1:
        return jsonify({'prediction': 'Jam'})


@app.route("/")
def run_main():
    main = Main()
    while True:
        startTime = datetime.datetime.now()
        print(f'{startTime}: Updating traffic stats...')
        main.update_stats()
        print(
            f'Stats updated. Time taken: {datetime.datetime.now() - startTime} minutes')
        print('Resting for 15 minutes...')
        time_wait = 15
        time.sleep(time_wait * 60)

@app.route("/incidents")
def get_incidents():
    traffic_incidents = pd.read_csv('./assets/incidents.csv')
    return jsonify(traffic_incidents.to_dict(orient="records"))

        
        
        
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
