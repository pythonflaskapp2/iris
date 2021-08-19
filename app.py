
from flask import Flask, jsonify,render_template,Request
from flask.globals import request
from jinja2 import exceptions
import json
from model.User import User
from validation.Validataor import *

app=Flask(__name__) 

@app.route('/users',methods = ["GET"])
@login_required
@admin_required
def getUsers():
    print(g.role)
    if (g.role == 'admin') :
        try:
            users = User.getUsers()
            output ={"Users":users}

            return jsonify(output),200
        except Exception as err:
            print(err)
            output = {"Message":"Error occurred"}
            return jsonify(output),500
    else:
        output = {"message":"You are not an authorized person to access this Service"}
        return jsonify(output),403
 
@app.route('/users/<int:userid>',methods = ["GET"])
@login_required
@require_isAdminOrSelf
def getOneUser(userid):
    print (g.role)
    if (g.role == 'admin') or (g.userid == userid):
        try:
            found = False
            userData =""
            users = User.getUserByUserid(userid)
            print("This is  practical5")
            if len(users)>0:
                output = {"Users":users}
                return jsonify(output),200
            else:
                output = {"Users":""}
                return jsonify(output),404
        except Exception as err:
            print(err)
            output = {"Message":"Error occurred"}
            return jsonify(output),500
    else:
        output = {"message":"You are not an authorized person to access this Service"}
        return jsonify(output),403
    
@app.route('/users/login',methods = ["POST"])
def loginUser():
    try:
            userData = request.json
            jwtToken= User.loginUser(userData['email'],userData['password'])
            output = {"JWT":jwtToken}
            return jsonify(output),200

    except Exception as err:
        print(err)
        output = {"Message":"Error occurred"}
        return jsonify(output),500     


if __name__ == '__main__':
    app.run(debug=True) #start the flask app with default port 5000
