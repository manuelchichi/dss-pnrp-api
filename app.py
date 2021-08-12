from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://api_user:password123@mongo:27017/api"
mongo = PyMongo(app)

@app.route("/")
def hello_world():
    return "<p>API is UP.</p>"

@app.route('/execution', methods=['POST'])
def post_route():
    if request.method == 'POST':
        data = mongo.db.execution.insert(request.get_json())
        print('Data Received: "{data}"'.format(data=data))
        return "Request Processed.\n"

@app.route('/get', methods=['GET'])
def get_route():
    if request.method == 'GET':

        data = {   
    "algorithms":
    [
        {
            "id": 1,
            "name": "NSGA-II",
            "version": "1.0",
            "parameters":
            [
                {"id": 1,
                 "name": "Poblacion",
                 "defaultValue": 100},
                {"id": 2,
                "name": "Generaciones",
                 "defaultValue": 50},
                {"id": 3,
                 "name": "Probabilidad de mutacion",
                 "defaultValue": 0.2},
                {"id": 4,
                 "name": "Ratio de Cruce",
                 "defaultValue": 0.8}
            ]
        },
        {
            "id": 2,
            "name": "MOPSO",
            "version": "1.0",
            "parameters":
            [
                {"id": 1,
                 "name": "Poblacion",
                 "defaultValue": 100},
                {"id": 2,
                 "name": "Generaciones",
                 "defaultValue": 70},
                {"id": 3,
                 "name": "Probabilidad de mutacion",
                 "defaultValue": 0.4},
                {"id": 4,
                 "name": "Ratio de Cruce",
                 "defaultValue": 0.8},
                {"id": 5,
                 "name": "Ratio de deterioro",
                 "defaultValue": 2}
            ]
        }
    ]
}
        print('Data sent')
        return jsonify(data)
