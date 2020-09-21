from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from bson.objectid import ObjectId
import static.forms as forms
import static.validations as val
import static.json as json_handler
import pymongo
import time

mb_user = "Vinicius"
pwd = "sYlrvbXJUtKyvwBZ"

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config["SECRET_KEY"] = "STRINGHARDTOGUESS"


client = pymongo.MongoClient("mongodb+srv://"+mb_user+":"+pwd+"@recdb.smlnb.mongodb.net/RecDB?retryWrites=true&w=majority")
db = client.RecDB

@app.route('/')
def index(methods=["GET","POST"]):
	return "",201

@app.route('/makeEvaluation',methods=["GET","POST"])
def makeEvaluation():	
	if request.content_type != "application/json":
		return "Bad Request. Content Type must be application/json", 400

	data = request.get_json()
	keys = ["user_id","colaborator_id","key","evaluation","comments","questions"]
	value_types = [str,str,str,float,str,list]

	#Validates JSON
	msg,flag = json_handler.validateJson(dict(data),keys,value_types)
	if flag != 201:
		return msg,flag

	#Validates Colaborator
	_application, flag = val.validateEvaluation(data["key"],
		                                        data["user_id"],
		                                        data["colaborator_id"],
		                                        data["questions"],
		                                        db)
	if flag != 201:
		return _application, flag

	if len(data["questions"]) < len(_application["questions"]):
		size1 = len(data["questions"])
		size2 = len(_application["questions"])
		return "Size of 'questions' list is {}, it should be {}".format(size1,size2),400

	_questions = {}
	count = 0
	for i in _application["questions"]:
		_questions[i]=data["questions"][count]
		count+=1

	query = db["Avaliacoes"].find_one({"app_id":ObjectId(_application["_id"]),
								   "user_id":ObjectId(data["user_id"]),
								   "colaborator_id":ObjectId(data["colaborator_id"])})
	if(query):
		db["Avaliacoes"].update_one(query,{"$set":{"evaluation":data["evaluation"],
												   "evaluation_time":time.time(),
												   "comments":data["comments"], 
												   "questions":_questions}})
		return "Evaluation updated succesfully",201
	else:
		
		_id = db["Avaliacoes"].insert_one({"app_id":ObjectId(_application["_id"]),
										   "user_id":ObjectId(data["user_id"]),
										   "colaborator_id":ObjectId(data['colaborator_id']),
										   "evaluation":data["evaluation"],
										   "evaluation_time":time.time(),
										   "comment":data["comments"],
										   "questions":_questions})
		return "Evaluation created succesfully",201


@app.route('/evaluationByApp',methods=["GET"])
def evaluationByApp():
	#Verifies the content of the request
	if request.content_type != "application/json":
		return "Bad Request. Content Type must be application/json", 400

	#Gets request JSON
	data = request.get_json()
	keys = ["app_id","colaborator_id"]
	value_types = [str,str]

	#Validates JSON
	msg,flag = json_handler.validateJson(dict(data),keys,value_types)
	if flag != 201:
		return msg,flag

	#Validates Application
	msg, flag = val.validateApplication(data["app_id"],db)
	if(flag != 201):
		return msg,flag
		
	#Validates Colaborator
	msg, flag = val.validateColaborator(data["colaborator_id"],db)
	if flag!=201:
		return msg, flag

	#Gets all evaluations to a specific APP
	query = db["Avaliacoes"].find({"app_id":ObjectId(data["app_id"]),"colaborator_id":ObjectId(data["colaborator_id"])},{"_id":0,"key":0})
	
	if(query):
		json = json_handler.evaluationJson(query)
		return jsonify(json),200
	else:
		return None,200

@app.route('/fullEvaluation',methods=["GET"])
def fullEvaluation():
	#Verifies the content of the request
	if request.content_type != "application/json":
		return "Bad Request. Content Type must be application/json", 400

	#Gets the request JSON
	data = request.get_json()
	keys = ["colaborator_id"]
	value_types = [str]

	#Validates the request JSON
	msg,flag = json_handler.validateJson(dict(data),keys,value_types)
	if flag != 201:
		return msg,flag

	#Validates Colaborator
	_colaborator, flag = val.validateColaborator(data["colaborator_id"],db)
	if flag!=201:
		return _colaborator, flag

	#Gets all evaluations made on this colaborator
	query = db["Avaliacoes"].find({"colaborator_id":ObjectId(data["colaborator_id"])},{"_id":0,"key":0})

	if(query):
		json = json_handler.evaluationJson(query)
		return jsonify(json), 200
	else:
		return None, 200

@app.route("/ManageColaborators",methods=["GET","POST","DELETE"])
def ManageColaborators():
	#Verifies the content of the request
	if request.content_type != "application/json":
		return "Bad Request. Content Type must be application/json", 400

	#Gets the request JSON
	data = request.get_json()
	keys = ["key","colaborator_list","status_list"]
	value_types = [str,list,list]
	
	#Validates the request JSON
	msg,flag = json_handler.validateJson(dict(data),keys,value_types)
	if flag != 201:
		return msg,flag	

	#Validates Key
	_application, flag = val.validateKey(data["key"],db)
	if flag != 201:
		return _application, flag

	#Validates User
	colaborators, flag = val.validateColaboratorList(data["colaborator_list"],db)
	if flag != 201:
		return colaborators, flag

	#Separates by method
	if request.method == "POST":
		
		#Updates the Database
		d={}
		for i in range(len(data["colaborator_list"])):
			d["colaborators."+data["colaborator_list"][i]] = data["status_list"][i]
		db["Applications"].update_one(_application,{"$set":d})
		return "Colaborators updated succesfully", 201

	elif request.method == "DELETE":
		#Updates the Database
		d={}
		for i in range(len(data["colaborator_list"])):
			d["colaborators."+data["colaborator_list"][i]] = ""
		db["Applications"].update_one(_application,{"$unset":d})

		return "",204

	elif request.method == "GET":
		d = {}
		for i in colaborators.keys():
			d[i]={}
			for j in colaborators[i]:
				if j != "_id":
					d[i][j]=colaborators[i][j]
		return d, 226