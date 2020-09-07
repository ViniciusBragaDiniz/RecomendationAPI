import pymongo
from bson.objectid import ObjectId

mb_user = "Vinicius"
pwd = "sYlrvbXJUtKyvwBZ"


invalid_colaborator = ("Invalid Colaborator ID, please check if Colaborator ID value is correct",401)
invalid_key = ("Invalid Aplication Key. Please check if Aplication Key value is correct",401)
invalid_user = ("Invalid User ID, please check if User ID value is correct",401)
invalid_app = ("Invalid APP ID, please check if APP ID value is correct",401)

def validateEvaluation(key,uid,eid):	
	
	try:
		query = db["Evaluators"].find_one({"_id":ObjectId(uid)})
		if(not query):
			return "Invalid User ID, please check if it was entered correctly",401
	except:
		return "Invalid User ID, please check if it was entered correctly",401
	
	try:
		query = db["Evaluated"].find_one({"_id":ObjectId(eid)})
		if(not query):
			return "Invalid Colaborator Id, please check if the id was entered correctly",401
	except:
		return "Invalid Colaborator Id, please check if the id was entered correctly",401

	return _application, 201

def validateKey(key):
	client = pymongo.MongoClient("mongodb+srv://"+mb_user+":"+pwd+"@recdb.smlnb.mongodb.net/RecDB?retryWrites=true&w=majority")
	db = client.RecDB
	
	try:
		_application = db["Applications"].find_one({"key":key})
		if(not _application):
			return invalid_key
		elif not _application["key_status"]:
			return "Your API access must be enabled. Please contact Support.",501
	except:
		client.close()
		return invalid_key

	client.close()
	return _application, 201

def validateColaborator(cid):
	client = pymongo.MongoClient("mongodb+srv://"+mb_user+":"+pwd+"@recdb.smlnb.mongodb.net/RecDB?retryWrites=true&w=majority")
	db = client.RecDB
	
	try:
		colaborator = db["Evaluated"].find_one({"_id":ObjectId(cid)})
		if(not colaborator):
			return invalid_colaborator
	except:
		return invalid_colaborator

	return colaborator, 201

def validateUser(uid):
	client = pymongo.MongoClient("mongodb+srv://"+mb_user+":"+pwd+"@recdb.smlnb.mongodb.net/RecDB?retryWrites=true&w=majority")
	db = client.RecDB
	
	try:
		user = db["Evaluators"].find_one({"_id":ObjectId(uid)})
		if(not user):
			return invalid_user
	except:
		return invalid_user

	return user, 201

def validateApplication(aid):
	client = pymongo.MongoClient("mongodb+srv://"+mb_user+":"+pwd+"@recdb.smlnb.mongodb.net/RecDB?retryWrites=true&w=majority")
	db = client.RecDB
	
	try:
		app = db["Applications"].find_one({"_id":ObjectId(aid)})
		if(not app):
			return invalid_app
	except:
		return invalid_app

	return app, 201

