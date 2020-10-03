from flask import Flask, jsonify, session, request, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from bson.objectid import ObjectId
import static.forms as forms
import static.validations as val
import static.json as json_handler
import static.CaptureOrder
import pymongo
import time
import secrets
import hashlib
import requests
import json

mb_user = "Vinicius"
pwd = "sYlrvbXJUtKyvwBZ"

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config["SECRET_KEY"] = "STRINGHARDTOGUESS"

client = pymongo.MongoClient("mongodb+srv://"+mb_user+":"+pwd+"@recdb.smlnb.mongodb.net/RecDB?retryWrites=true&w=majority")
db = client.RecDB

@app.route('/',methods=["GET","POST"])
def index():
	form = forms.userLogin()
	if form.validate_on_submit():
		email = form.email.data
		data = db["Users"].find_one({"user_email":email})
		userdata = User(username=data["name"],email=data["user_email"])
		client.close()
		return str(userdata.username)
	return render_template("base.html",form=form, name=session.get("name"),user=session.get("user"))
		
@app.route('/user',methods=["GET","POST"])
def user():
	form = forms.userSignUp()
	form2 = forms.userLogin()
	
	return render_template("index.html",form=form,form2=form2,signUp = "userSignUp", signIn = "userSignIn", name=session.get("name"),user=session.get("user"))
@app.route('/userSignUp', methods=["GET","POST"])
def userSignUp():
	form = forms.userSignUp()
	form2 = forms.userLogin()

	if form.validate_on_submit():
		name = form.name.data
		email = form.email.data
		pswd = hashlib.sha256(form.pswd.data.encode()).hexdigest()

		query = db["Users"].find_one({"user_email":email})
		if(query):
			flash(str(query["_id"]))
		else:
			flash(str(db["Users"].insert_one({"name":name,"user_email":email,"user_pswd":pswd}).inserted_id))

	return render_template("index.html",form=form,form2=form2,signUp = "userSignUp", signIn = "userSignIn", name=session.get("name"),user=session.get("user"))

@app.route('/userSignIn', methods=["GET","POST"])
def userSignIn():
	form = forms.userSignUp()
	form2 = forms.userLogin()

	email = request.form["login_email"]
	pswd = hashlib.sha256(request.form["login_pswd"].encode()).hexdigest()
	
	query = db["Users"].find_one({"user_email":email,"user_pswd":pswd})
	if(query):
		session["_id"] = str(query["_id"])
		session["name"] = str(query["name"])
		session["user"] = "user"
	else:
		flash("Incorrect E-mail or Password.")

	return render_template("index.html",form=form,form2=form2,signUp = "userSignUp", signIn = "userSignIn", name=session.get("name"),user=session.get("user"))

@app.route('/colaborator',methods=["GET","POST"])
def colaborator():
	form = forms.colaboratorSignUp()
	form2 = forms.userLogin()
	if form.validate_on_submit():
		name = form.name.data
		email = form.email.data
		pswd = hashlib.sha256(form.pswd.data.encode()).hexdigest()
		
		query = db["Colaborators"].find_one({"user_email":email})
		if(query):
			flash("User already exists.")
		else:
			return str(db["Colaborators"].insert_one({"name":name,"user_email":email,"user_pswd":pswd}).inserted_id)

	return render_template("index.html",form=form,form2=form2,signUp = "colaboratorSignUp", signIn="colaboratorSignIn", name=session.get("name"),user=session.get("user"))

@app.route('/colaboratorSignUp', methods=["GET","POST"])
def colaboratorSignUp():
	name = request.form["name"]
	email = request.form["email"]
	psw = hashlib.sha256(frequest.form["pswd"].encode()).hexdigest()

	query = db["Colaborators"].find_one({"user_email":email})
	if(query):
		flash("User already exists.")
	else:
		return str(db["Colaborators"].insert_one({"name":name,"user_email":email,"user_pswd":pswd}).inserted_id)

	return render_template("index.html",form=form,form2=form2,signUp = "colaboratorSignUp", signIn="colaboratorSignIn", name=session.get("name"),user=session.get("user"))

@app.route('/colaboratorSignIn', methods=["GET","POST"])
def colaboratorSignIn():
	form = forms.userSignUp()
	form2 = forms.userLogin()

	email = request.form["login_email"]
	pswd = hashlib.sha256(request.form["login_pswd"].encode()).hexdigest()
	
	query = db["Colaborators"].find_one({"user_email":email,"user_pswd":pswd})
	if(query):
		session["_id"] = str(query["_id"])
		session["name"] = str(query["name"])
		session["user"] = "colab"
	else:
		flash("Incorrect E-mail or Password.")


	return render_template("index.html",form=form,form2=form2,signUp = "colaboratorSignUp", signIn="colaboratorSignIn", name=session.get("name"),user=session.get("user"))

@app.route('/application',methods=["GET","POST"])
def application():
	form = forms.applicationSignUp()
	form2 = forms.userLogin()

	return render_template("index.html",form=form,form2=form2,signUp = "appSignUp", signIn="appSignIn", name=session.get("name"),user=session.get("user"))

@app.route('/appSignUp',methods=["GET","POST"])
def appSignUp():
	name = request.form["name"]
	email = request.form["email"]
	psw = hashlib.sha256(frequest.form["pswd"].encode()).hexdigest()
	question = request.form["question"].split(",")
	
	query = db["Applications"].find_one({"name":name})
	if(query):
		return "Application already exists, please check if the key entered is correct and try again."

	else:
		return "Cadastro realizado com sucesso!\n"+str(db["Applications"].insert_one({"name":name,
																					  "user_email":email,
																					  "user_psw":psw,
																					  "key":None,
																					  "key_status":False,
																					  "limit":0,
																					  "requisitions":0,
																					  "questions":question}).inserted_id)
	return render_template("index.html",form=form,form2=form2,signUp = "appSignUp", signIn="appSignIn",name=session.get("name"),user=session.get("user"))

@app.route('/appSignIn', methods=["GET","POST"])
def appSignIn():
	form = forms.userSignUp()
	form2 = forms.userLogin()

	email = request.form["login_email"]
	pswd = hashlib.sha256(request.form["login_pswd"].encode()).hexdigest()
	
	query = db["Applications"].find_one({"user_email":email,"user_pswd":pswd})
	if(query):
		session["_id"] = str(query["_id"])
		session["name"] = str(query["name"])
		session["user"] = "app"
		session["key"] = str(query["key"])
	else:
		flash("Incorrect E-mail or Password.")

	return redirect(url_for("appInfo"))
@app.route('/logout',methods=["GET","POST"])
def logout():
	session.clear()
	return redirect(url_for("application"))
@app.route('/buy',methods=["GET","POST"])
def buy():
	if session.get("_id"):
		form = forms.payment()
		if form.validate_on_submit():
			data = db["Applications"].find_one({"_id":ObjectId(session.get("_id"))})
			if data:
				session["key_type"] = form.key_type.data
				return redirect(url_for("payment"))

			else:
				flash("Application don't exists")
				return redirect(url_for("application",
										form=forms.applicationSignUp(), form2=forms.userLogin()), 
										name=session.get("name"),user=session.get("user"))

		return render_template("base.html",form=form,  name=session.get("name"),user=session.get("user"))
	else:
		flash("Você não está logado!")
		return redirect(url_for("application",
										form=forms.applicationSignUp(), form2=forms.userLogin()), 
										name=session.get("name"),user=session.get("user"))

@app.route('/appInfo',methods=["GET","POST"])
def appInfo():
	form = forms.searchColab()
	form2 = forms.manageColab()
	urls=["/appInfo/Buscar","/appInfo/Cadastrar","/appInfo/Atualizar","/appInfo/Remover"]
	return render_template("app_info.html",form=form, form2 = form2, name=session.get("name"),user=session.get("user"), info=None)

@app.route('/appInfo/Procurar',methods=["GET","POST"])
def appInfoBuscar():
	form = forms.searchColab()
	form2 = forms.manageColab()
	try:
		query = db["Colaborators"].find_one({"_id":ObjectId(request.form["cid"])})
		if query:
			info = {}
			info["User Name"] = query["name"]
			info["User E-Mail"] = query["user_email"]
			info["Questions"] = db["Applications"].find_one({"_id":ObjectId(session.get("_id"))},{"questions":1,"_id":0})["questions"]

			new_query = db["Avaliacoes"].find({"colaborator_id":ObjectId(request.form["cid"]),"app_id":ObjectId(session.get("_id"))})
			if new_query:
				info["evaluation"] = []
				count=0
				for i in new_query:
					info["evaluation"].append({"Avaliação":i["evaluation"],
											 "Horário":time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(i["evaluation_time"])),
											 "Comentário":i["comment"]})

					if len(i["questions"]) > 0:
						for j in i["questions"]:
							info["evaluation"][count][j] = i["questions"][j] 
					count+=1
			else:
				info["evaluation"] = None



			return render_template("app_info.html",form=form, form2 = form2, name=session.get("name"),user=session.get("user"), info=info)
		else:
			flash("ID Inválido, não foi possível encontrar o colaborador")
			return redirect(url_for("appInfo"))
	except:
		flash("ID Inválido, não foi possível encontrar o colaborador")
		return redirect(url_for("appInfo"))
	return render_template("app_info.html",form=form, form2 = form2, name=session.get("name"),user=session.get("user"), info=None)



@app.route('/appInfo/Cadastrar',methods=["GET","POST"])
def appInfoCadastrar():
	form = forms.searchColab()
	form2 = forms.manageColab()
	
	colaborator_list = request.form["cid"].split(',')
	status_list = request.form["status"].split(',')

	body = {"key":session.get("key"),"colaborator_list":colaborator_list,"status_list":status_list}

	res= requests.post("https://recomendation-api-cefet.herokuapp.com/ManageColaborators",data=json.dumps(body),headers={"content-type":"application/json"})

	flash(res.text)
	return render_template("app_info.html",form=form, form2 = form2, name=session.get("name"),user=session.get("user"), info=None)

@app.route('/appInfo/Atualizar', methods=["GET","POST"])
def appInfoAtualizar():
	form = forms.searchColab()
	form2 = forms.manageColab()
	
	colaborator_list = request.form["cid"].split(',')
	status_list = request.form["status"].split(',')

	body = {"key":session.get("key"),"colaborator_list":colaborator_list,"status_list":status_list}

	res= requests.post("https://recomendation-api-cefet.herokuapp.com/ManageColaborators",data=json.dumps(body),headers={"content-type":"application/json"})

	flash(res.text)
	return render_template("app_info.html",form=form, form2 = form2, name=session.get("name"),user=session.get("user"), info=None)


@app.route('/appInfo/Remover',methods=["GET","POST","DELETE"])
def appInfoRemover():
	form = forms.searchColab()
	form2 = forms.manageColab()
	
	colaborator_list = request.form["cid"].split(',')
	status_list = []

	body = {"key":session.get("key"),"colaborator_list":colaborator_list,"status_list":status_list}

	requests.delete("https://recomendation-api-cefet.herokuapp.com/ManageColaborators",data=json.dumps(body),headers={"content-type":"application/json"})

	flash("Colaborator removed sucessfully")
	return render_template("app_info.html",form=form, form2 = form2, name=session.get("name"),user=session.get("user"), info=None)

@app.route('/payment',methods=["GET","POST"])
def payment():
	key_type = int(session.get("key_type"))
	if key_type == 1:
		value = 100.00
	elif key_type == 2:
		value = 195.00
	elif key_type == 3:
		value = 250.00
	return render_template('payment.html',value=value, name=session.get("name"),user=session.get("user"))

@app.route('/confirmPayment',methods=["GET","POST"])
def confirm():
	data = request.get_json()
	response = CaptureOrder().capture_order(data["orderID"],
											client.OrdersDB,
											db,
											session.get("_id"),
											int(session.get("key_type")),
											debug=True)
	return "Sucess",201


