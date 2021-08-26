
from flask import Flask, jsonify,render_template,Request
from flask.globals import request
from jinja2 import exceptions
import json
from model.User import User
from validation.Validataor import *
import numpy as np
#from flask_cors import CORS

app=Flask(__name__) 
#CORS(app)

    
@app.route('/login', methods =["GET","POST"])
def login():
    try:
        print("login")
        if request.method == "POST":
            print(request.form['email']) 
            print("post")
            table = {}
            for i in np.arange(5):
                print (i)
                n= (i+1)*5
                print(n)
                table[i+1] = n
            print (table)
            email = request.form['email']
            password = request.form['password']
            print("after form submit", email)
            jwtToken= User.loginUser(email,password)
            print ("JWT",jwtToken)
            if (jwtToken != ""):
                return render_template("mainPage.html",username = jwtToken[1], table=table)
            else:
                print("no match")
                return render_template ("login.html",message = "Invalid Login Credentials!")
    except Exception as err:
        print(err)
        output = {"Message":"Error occurred"}
        return jsonify(output),500  
    return render_template('login.html')   


if __name__ == '__main__':
    app.run(debug=True) #start the flask app with default port 5000
