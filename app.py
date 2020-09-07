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

@app.route('/')
def index(methods=["GET","POST"]):
	return redirect(url_for("userSignUp"))
@app.route('/makeEvaluation',methods=["GET","POST"])
def makeEvaluation():
	client = pymongo.MongoClient("mongodb+srv://"+mb_user+":"+pwd+"@recdb.smlnb.mongodb.net/RecDB?retryWrites=true&w=majority")
	db = client.RecDB
	
	data = request.get_json()
	keys = ["user_id","colaborator_id","key","evaluation","comments","questions"]
	value_types = [str,str,str,float,str,dict]
	msg,flag = json_handler.validateJson(dict(data),keys,value_types)
	if flag != 201:
		client.close()
		return msg,flag

	uid = data["user_id"]
	cid = data["colaborator_id"]
	key = data["key"]
	e= data["evaluation"]
	comment = data["comments"]
	q = data["questions"]

	#Validates User
	user, flag = val.validateUser(uid)
	if flag != 201:
		client.close()
		return user, str(flag)

	#Validates Colaborator
	collaborator, flag = val.validateColaborator(cid)
	if flag != 201:
		client.close()
		return collaborator, flag

	#Validates Key
	_application, flag = val.validateKey(key)
	if flag != 201:
		client.close()
		return _application, flag

	aid = _application["_id"]
	query = db["Avaliacoes"].find_one({"key":key,"user_id":ObjectId(uid),"colaborator_id":ObjectId(cid)})
	if(query):
		db["Avaliacoes"].update_one(query,{"$set":{"evaluation":e,"evaluation_time":time.time(),"comment":comment}})
	else:
		_questions = {}
		count = 0
		for i in _application["questions"]:
			_questions[i]=q[count]
			count+=1
		_id = db["Avaliacoes"].insert_one({"app_id":ObjectId(aid),
										   "user_id":ObjectId(uid),
										   "colaborator_id":ObjectId(cid),
										   "evaluation":e,
										   "evaluation_time":time.time(),
										   "comment":comment,
										   "questions":_questions})
		return "Sucess!", 201
	client.close()

@app.route('/evaluationByApp',methods=["GET"])
def evaluationByApp():
	client = pymongo.MongoClient("mongodb+srv://"+mb_user+":"+pwd+"@recdb.smlnb.mongodb.net/RecDB?retryWrites=true&w=majority")
	db = client.RecDB
	dbcollection = db.Evaluated

	data = request.get_json()
	keys = ["app_id","colaborator_id"]
	value_types = [str,str]
	msg,flag = json_handler.validateJson(dict(data),keys,value_types)
	if flag != 201:
		client.close()
		return msg,flag


	_application, flag = val.validateApplication(data["app_id"])

	if(flag == 201):
		
		_colaborator, flag = val.validateColaborator(data["colaborator_id"])
		if flag!=201:
			return _colaborator, flag

		query = db["Avaliacoes"].find({"app_id":ObjectId(data["app_id"]),"colaborator_id":ObjectId(data["colaborator_id"])},{"_id":0,"key":0})
		if(query):
			
			json = json_handler.evaluationJson(query)
			client.close()
			return jsonify(json)
	else:
		client.close()
		return _application, flag

@app.route('/fullEvaluation',methods=["GET"])
def fullEvaluation():
	
	client = pymongo.MongoClient("mongodb+srv://"+mb_user+":"+pwd+"@recdb.smlnb.mongodb.net/RecDB?retryWrites=true&w=majority")
	db = client.RecDB
		
	data = request.get_json()
	keys = ["colaborator_id"]
	value_types = [str]
	msg,flag = json_handler.validateJson(dict(data),keys,value_types)
	if flag != 201:
		client.close()
		return msg,flag

	_colaborator, flag = val.validateColaborator(data["colaborator_id"])
	if flag!=201:
		return _colaborator, flag

	query = db["Avaliacoes"].find({"colaborator_id":ObjectId(data["colaborator_id"])},{"_id":0,"key":0})
	if(query):
		
		json = json_handler.evaluationJson(query)
		client.close()
		return jsonify(json), 200

@app.route('/InsertOrUpdateColaborator')
def insertColaborator():
	client = pymongo.MongoClient("mongodb+srv://"+mb_user+":"+pwd+"@recdb.smlnb.mongodb.net/RecDB?retryWrites=true&w=majority")
	db = client.RecDB

	data = request.get_json()
	keys = ["key","colaborator_id","status"]
	value_types = [str,str,str]
	msg,flag = json_handler.validateJson(dict(data),keys,value_types)
	if flag != 201:
		client.close()
		return msg,flag	

	#Validates User
	collaborator, flag = val.validateColaborator(data["colaborator_id"])
	if flag != 201:
		client.close()
		return collaborator, flag

	#Validates Key
	_application, flag = val.validateKey(data["key"])
	if flag != 201:
		client.close()
		return _application, flag

	query_app = db["Applications"].find_one({"key":data["key"]})

	db["Applications"].update_one(query_app,{"$set":{"colaborators."+data["colaborator_id"]:data["status"]}})

	return "Colaborator updated succesfully", 201

@app.route('/RemoveColaborator')
def removeColaborator():
	client = pymongo.MongoClient("mongodb+srv://"+mb_user+":"+pwd+"@recdb.smlnb.mongodb.net/RecDB?retryWrites=true&w=majority")
	db = client.RecDB

	data = request.get_json()
	keys = ["key","colaborator_id"]
	value_types = [str,str]
	msg,flag = json_handler.validateJson(dict(data),keys,value_types)
	if flag != 201:
		client.close()
		return msg,flag

	#Validates User
	collaborator, flag = val.validateColaborator(data["colaborator_id"])
	if flag != 201:
		client.close()
		return collaborator, flag

	#Validates Key
	_application, flag = val.validateKey(data["key"])
	if flag != 201:
		client.close()
		return _application, flag

	query_app = db["Applications"].find_one({"key":data["key"]})

	db["Applications"].update_one(query_app,{"$unset":{"colaborators."+data["colaborator_id"]:""}})

	return "Colaborator updated succesfully", 201

@app.route('/userSignUp',methods=["GET","POST"])
def userSignUp():
	form = forms.userSignUp()
	if form.validate_on_submit():
		client = pymongo.MongoClient("mongodb+srv://"+mb_user+":"+pwd+"@recdb.smlnb.mongodb.net/RecDB?retryWrites=true&w=majority")
		db = client.RecDB
		dbcollection = db.Evaluators
		name = form.name.data
		user_email = form.user_email.data
		pswd = form.user_pswd.data

		query = db["Evaluators"].find_one({"user_email":user_email})
		if(query):

			client.close()
			return str(query["_id"])
		else:

			client.close()
			return str(dbcollection.insert_one({"name":name,"user_email":user_email}).inserted_id)

	return render_template("index.html",form=form)

@app.route('/colaboratorSignUp',methods=["GET","POST"])
def colaboratorSignUp():
	form = forms.colaboratorSignUp()
	if form.validate_on_submit():
		client = pymongo.MongoClient("mongodb+srv://"+mb_user+":"+pwd+"@recdb.smlnb.mongodb.net/RecDB?retryWrites=true&w=majority")
		db = client.RecDB
		dbcollection = db.Evaluated
		name = form.name.data
		email = form.user_email.data
		pswd = form.user_pswd.data
		
		query = db["Evaluated"].find_one({"email":email})
		if(query):

			client.close()
			raise Exception("User already exists, please check if the e-mail entered is correctly and try again.")
		else:

			client.close()
			return str(dbcollection.insert_one({"name":name}).inserted_id)

	return render_template("index.html",form=form)

@app.route('/applicationSignUp',methods=["GET","POST"])
def applicationSignUp():
	form = forms.applicationSignUp()
	if form.validate_on_submit():
		client = pymongo.MongoClient("mongodb+srv://"+mb_user+":"+pwd+"@recdb.smlnb.mongodb.net/RecDB?retryWrites=true&w=majority")
		db = client.RecDB
		
		name = form.name.data
		key = form.key.data
		key_status = form.key_status.data
		question = form.questions.data.split(",")
		
		query = db["Applications"].find_one({"key":key})
		if(query):

			client.close()
			raise Exception("Application already exists, please check if the key entered is correct and try again.")
		else:

			client.close()
			return str(db["Applications"].insert_one({"name":name}).inserted_id)

	return render_template("index.html",form=form)


