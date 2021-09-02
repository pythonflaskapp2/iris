
from email import message
from flask import Flask, jsonify,render_template,Request, redirect, url_for, make_response
from flask.globals import request
from jinja2 import exceptions
import json
from model.User import User
from validation.Validataor import *
import numpy as np
from flask_cors import CORS
import pickle
import pandas as pd
from flask_mail import Message, Mail
from time import time
from flask import g

app=Flask(__name__) 
app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'irisflowerprediction@gmail.com',
    MAIL_PASSWORD = 'IrisFlower!@#',
))
mail = Mail(app)
CORS(app)
#global reset_password_userid

@app.route('/')
def homepage():
    return render_template('login.html')


@app.route('/predictPage', methods=["GET","POST"])
@login_required
def predictPage():
    try:
        print("render")
        if request.method == "POST":

            sepal_length = float(request.form['sepal-length'])
            print("inputs",sepal_length)
            sepal_width = float(request.form['sepal-width'])
            petal_length = float(request.form['petal-length'])
            petal_width = float(request.form['petal-width'])
            userid = request.cookies.get('userid')
    
            predictions = User.predictIris(sepal_length,sepal_width,petal_length,petal_width,userid)
            print("prediction full", predictions[2])
            username = request.cookies.get('username')
            jwt = request.cookies.get('jwt')
            if predictions != " ":
                prob = "Prediction Probability is {0} %".format(round(predictions[1],2))
                print(prob)
                return render_template('mainPage.html', predictions = predictions[0], prob = prob,result=predictions[2],username=username,jwt=jwt)
        elif request.method == "GET":
            print("after login get")
            userid = request.cookies.get('userid')
            predictions = User.getPredictions(userid)
            username = request.cookies.get('username')
            jwt = request.cookies.get('jwt')
            if predictions != " ":
                return render_template('mainPage.html',result=predictions,username=username,jwt=jwt)
            else:
                return render_template('mainPage.html',result="",username=username,jwt=jwt)
    except Exception as err:
        print(err)
        output = {"Message":"Error occurred"}
        return jsonify(output),500  
    
        
        
@app.route('/register', methods=["GET","POST"])
def register():
    
    if request.method == "POST":

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        count = User.insertUser(username,email,password)
        print(count)
        if count == " " :
            
            return render_template('register.html', message="Error Occured")
        else:
            return render_template("login.html",message="Login again ")
    return render_template('register.html')

@app.route('/logout',methods=['GET','POST'])
def logout():
    try:
        resp = make_response(render_template('login.html'))
        resp.set_cookie('jwt','')
        return resp
    except Exception as err:
        output = {"Message":"Error occurred"}
        return jsonify(output),500  
        
@app.route('/login', methods =["GET","POST"])
def login():
    try:
        print("login")
        print(request.method)
        if request.method == "POST":
 
            print(request.form['email']) 
            email = request.form['email']
            password = request.form['password']
            print("after form submit", email)
            jwtToken= User.loginUser(email,password)
            print ("JWT",jwtToken)
            if jwtToken == " " or jwtToken == "Wrong Password":
                return render_template ("login.html",message = "Invalid Login Credentials!")
            else:

                print("login else")
                email = request.form["email"]
                predictions = User.getPredictionsUsingEmail(str(email))
                username = request.cookies.get('username')
                jwt = request.cookies.get('jwt')
                if predictions != " ":
                    print("first time login")
                    resp = make_response(render_template("mainPage.html",result=predictions,username=jwtToken[1],jwt=jwt))
                    resp.set_cookie('jwt',jwtToken[0])
                    resp.set_cookie('username',jwtToken[1])
                    resp.set_cookie('userid',str(jwtToken[2]))
                    print("set")                
                    return resp
                else:
                    return render_template('mainPage.html',result="",username=username,jwt=jwt)
                return resp
     
            
        #if(request.method == "GET"):
         #   print("GET insdie")
          #  return render_template('login.html') 
    except Exception as err:
        print(err)
        output = {"Message":"Error occurred"}
        return jsonify(output),500  
    return render_template('login.html')   
    #return redirect(url_for("login"))


@app.route("/deletePrediction", methods =["DELETE"])
def deletePrediction():
    try:
        if request.method == "DELETE":

            pid= request.json['predictionid']

            response = User.deletePrediction(str(pid))
            print(response)
            if response[0]:
                return  response[1]
    except Exception as err:
        output ={"Message":"Error Occured"}
        return jsonify(output,500)

@app.route('/password_reset', methods=['GET','POST'])
def password_reset():
    try:
        if request.method == 'POST':
            email = request.form['email']
            print("email",email)
            user,count= User.verify_email(email)
            print("count",count)
            print("username",user['username'])
            
            global reset_password_userid
            reset_password_userid = int(user['userid'])
            print("global userid")
            if count:
               send_email(user)
               # Thread(target=send_email, args=(app, msg)).start()
               
            return render_template('login.html',message="Email Sent. Please check your inbox")
    except Exception as err:
        output ={"Message":err}
        return jsonify(output,500)
    
@app.route('/forgot_password', methods=['GET','POST'])
def forgot_password():
    try:
        print("password reset")
        return render_template('password_reset.html')
          
    except Exception as err:
        output ={"Message":err}
        return jsonify(output,500)

@app.route('/reset_verified/<token>', methods=['POST','GET'])
def reset_verified(token):

    email = jwt.decode(token, key=Settings.secretKey)['reset_password']
    print (email)
    user = User.verify_username
    if user == " ":
        #return render_template('login.html',message="Mail sent. Please check your inbox")
        return render_template('login.html',message="No user found")
    
    
    return render_template('new_password.html',email=email)

@app.route('/update_password', methods=['GET','POST'])
def update_password():
    newpassword = request.form['newpassword']
    cnewpassword = request.form['cnewpassword']
    email = request.form['email']
    if newpassword != cnewpassword:
        return render_template('new_password.html',message="Passwords do not match")
    else:

        resp = User.updatePassword(email,newpassword)
        if resp:
           return render_template('login.html',message="Password Updated")
       
def send_email(user):

    token = jwt.encode({'reset_password':user['email'],'exp':time()+500},
                    key = Settings.secretKey)
    print("token",token)
    mail_id = user['email']

    print(app.config['MAIL_USERNAME'])
    msg = Message()
    msg.subject="Password Reset"
    msg.sender = app.config['MAIL_USERNAME']
    msg.recipients = [mail_id]
    msg.html = render_template('reset_email.html',user=user['username'],token=token)
    print("msg",msg.html)
    mail.send(msg)
            


if __name__ == '__main__':
    app.run(debug=True) #start the flask app with default port 5000

