from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_expects_json import expects_json
import numpy as np
import pandas as pd
import itertools


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://api_user:password123@mongo:27017/api"
mongo = PyMongo(app)

@app.route("/health")
def health():
    return "<p>OK</p>"

schema = {
    "type": "object",
    "properties": {
        "criteria": {"type": "object"},
        "issues": {"type": "array",
                   "items": {"type": "object",
                             "properties": {
                                    "id": {"type": "number"},
                                    "eval": {"type": "object"}
                                    }
                            }
                  }
    },
    "required": ["criteria", "issues"]
}

@app.route('/execution', methods=['POST'])
@expects_json(schema)
def post_execution():
    if request.method == 'POST':
        data = request.get_json()
        #data = mongo.db.execution.insert(request.get_json())
        #print('Data Received: "{data}"'.format(data=data))
        return "Request Processed.\n"

@app.route('/getSolutions/<int:prp_process_id>', methods=['GET'])
def get_solutions(prp_process_id):
    if request.method == 'GET':
        data = {
                "id":1,
                "prp_process_id":1,
                "executions":
                 [
                     {
                       "id":1,
                       "status":"finished",
                       "alternatives":
                       [
                           {
                               "alternative_id":1,
                               "issues":
                               [
                                   {
                                       "issue_id":1,
                                       "priority_id": 1
                                   },
                                   {
                                       "issue_id":2,
                                       "priority_id": 2
                                   },
                                   {
                                       "issue_id":3,
                                       "priority_id": 1
                                   },
                                   {
                                       "issue_id":4,
                                       "priority_id": 2
                                   },
                                   {
                                       "issue_id":5,
                                       "priority_id": 3
                                   }
                               ]
                           },
                           {
                               "alternative_id":2,
                               "issues":
                               [
                                   {
                                       "issue_id":1,
                                       "priority_id": 3
                                   },
                                   {
                                       "issue_id":2,
                                       "priority_id": 2
                                   },
                                   {
                                       "issue_id":3,
                                       "priority_id": 2
                                   },
                                   {
                                       "issue_id":4,
                                       "priority_id": 1
                                   },
                                   {
                                       "issue_id":5,
                                       "priority_id": 1
                                   }
                               ]
                           }
                       ]
                     },
                     {
                       "id":2,
                       "status":"finished",
                       "alternatives":
                       [
                           {
                               "alternative_id":1,
                               "issues":
                               [
                                   {
                                       "issue_id":1,
                                       "priority_id": 1
                                   },
                                   {
                                       "issue_id":2,
                                       "priority_id": 2
                                   },
                                   {
                                       "issue_id":3,
                                       "priority_id": 1
                                   },
                                   {
                                       "issue_id":4,
                                       "priority_id": 2
                                   },
                                   {
                                       "issue_id":5,
                                       "priority_id": 3
                                   }
                               ]
                           }
                       ]
                     }
                 ]
              }
        return jsonify(data)

@app.route('/getAlgorithms', methods=['GET'])
def get_algorithms():
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
        return jsonify(data)