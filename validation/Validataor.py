from flask import Flask,jsonify,render_template,request,g
from config.Settings import Settings
import functools
import jwt


def login_required(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        # Do something before
        token=request.headers.get('Authorization')
        auth=True
        #print(token.index("Bearer"))
        if token and token.index("Bearer")==0:
            token=token.split(" ")[1]
        else:
            auth=False
        if auth:
            try:
                #decode
                payload=jwt.decode(token,Settings.secretKey,"HS256")

                g.role=payload['role']
                g.userid=payload['userid']
                
            except jwt.exceptions.InvalidSignatureError as err:
                print(err)
                auth=False
        
        if auth==False:
            output={"Message":"Error JWT"}
            return jsonify(output),403
        
        value = func(*args, **kwargs)
        # Do something after
        return value
    return wrapper_decorator

def admin_required(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        token = request.headers.get("Authorization")
        auth = True
        if token and token.index("Bearer")==0:
            token = token.split(" ")[1]
        else:
            auth = False
        if auth:
            try:
                payload = jwt.decode(token, Settings.secretKey,"HS256")
                g.role = payload['role']

            except jwt.ExpiredSignatureError as err:
                print(err)
                auth = False
        value = func(*args, **kwargs)
        print("Value",value)
        return value
    print("wrapper",wrapper_decorator)
    
    return wrapper_decorator

def require_isAdminOrSelf(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        token = request.headers.get("Authorization")
        auth = True
        if token and token.index("Bearer")==0:
            token = token.split(" ")[1]
        else:
            auth = False
        if auth:
            try:
                payload = jwt.decode(token, Settings.secretKey,"HS256")
                #g.role = payload['role']
                g.role = payload['role']
                g.userid = payload['userid']
            except jwt.ExpiredSignatureError as err:
                print(err)
                auth = False
        value = func(*args, **kwargs)
        return value
    return wrapper_decorator



