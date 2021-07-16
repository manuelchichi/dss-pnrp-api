from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World! asdasdas</p>"

@app.route('/post', methods=['POST'])
def post_route():
    if request.method == 'POST':

        data = request.get_json()
        print('Data Received: "{data}"'.format(data=data))
        return "Request Processed.\n"

@app.route('/ping')
def ping():
	return jsonify({   
    "algorithms":
    [
        {
            "id": 1,
            "name": "NSGA-II",
            "version": "1.0",
            "parameters":
            [
                {"name": "Poblacion",
                 "defaultValue": 100},
                {"name": "Generaciones",
                 "defaultValue": 50},
                {"name": "Probabilidad de mutacion",
                 "defaultValue": 0.2},
                {"name": "Ratio de Cruce",
                 "defaultValue": 0.8}
            ]
        },
        {
            "id": 2,
            "name": "MOPSO",
            "version": "1.0",
            "parameters":
            [
                {"name": "Poblacion",
                 "defaultValue": 100},
                {"name": "Generaciones",
                 "defaultValue": 70},
                {"name": "Probabilidad de mutacion",
                 "defaultValue": 0.4},
                {"name": "Ratio de Cruce",
                 "defaultValue": 0.8},
                {"name": "Ratio de deterioro",
                 "defaultValue": 2}
            ]
        }
    ]
}
)

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
                {"name": "Poblacion",
                 "defaultValue": 100},
                {"name": "Generaciones",
                 "defaultValue": 50},
                {"name": "Probabilidad de mutacion",
                 "defaultValue": 0.2},
                {"name": "Ratio de Cruce",
                 "defaultValue": 0.8}
            ]
        },
        {
            "id": 2,
            "name": "MOPSO",
            "version": "1.0",
            "parameters":
            [
                {"name": "Poblacion",
                 "defaultValue": 100},
                {"name": "Generaciones",
                 "defaultValue": 70},
                {"name": "Probabilidad de mutacion",
                 "defaultValue": 0.4},
                {"name": "Ratio de Cruce",
                 "defaultValue": 0.8},
                {"name": "Ratio de deterioro",
                 "defaultValue": 2}
            ]
        }
    ]
}
        print('Data sent')
        return jsonify(data)
