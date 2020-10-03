import pymongo
from bson.objectid import ObjectId

mb_user = "Vinicius"
pwd = "sYlrvbXJUtKyvwBZ"


invalid_colaborator = ("Invalid Colaborator ID, please check if Colaborator ID value is correct",401)
invalid_colaborator_at_position = "Invalid Colaborator ID at position: "
invalid_user_at_position = "Invalid User ID at position: "
invalid_key = ("Invalid Aplication Key. Please check if Aplication Key value is correct",401)
deactivated_key = ("Your API access must be enabled. Please contact Support.",501)
invalid_question = ("Invalid Question Type {} at position: {}",401)
invalid_user = ("Invalid User ID, please check if User ID value is correct",401)
invalid_app = ("Invalid APP ID, please check if APP ID value is correct",401)

def validateKey(key,db):
	try:
		_application = db["Applications"].find_one({"key":key})

		if(not _application):
			return invalid_key

		elif not _application["key_status"]:
			return deactivated_key
		
		return _application, 201
	except:
		return invalid_key	

def validateColaborator(cid,db):
	try:
		colaborator = db["Colaborators"].find_one({"_id":ObjectId(cid)})

		if(not colaborator):
			return invalid_colaborator

		return colaborator, 201

	except:
		return invalid_colaborator	

def validateColaboratorList(cid_list,db):
	d = {}
	for i in range(len(cid_list)):
		try:
			colaborator = db["Colaborators"].find_one({"_id":ObjectId(cid_list[i])})
			if(not colaborator):
				return invalid_colaborator_at_position+str(i),401
			else:
				d[cid_list[i]]=colaborator
		except:
			return invalid_colaborator_at_position+str(i),401

	return d, 201

def validateUser(uid,db):
	try:
		user = db["Users"].find_one({"_id":ObjectId(uid)})
		if(not user):
			return invalid_user
	except:
		return invalid_user

	return user, 201

def validateApplication(aid,questions,db):
	try:
		app = db["Applications"].find_one({"_id":ObjectId(aid)})
		if(not app):
			return invalid_app

		if questions:
			for i in range(len(questions)):
				if type(questions[i]) != str:
					return invalid_question[0].format(type(questions[i]),i),invalid_question[1]

	except:
		return invalid_app

	return app, 201
