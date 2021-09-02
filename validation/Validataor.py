from flask import Flask,jsonify,render_template,request,g
from werkzeug.utils import redirect
from config.Settings import Settings
import functools
import jwt


def login_required(func):
    @functools.wraps(func)
    def secure_login(*args, **kwargs):
        # Do something before
        auth=True
        auth_token = request.cookies.get('jwt')
        print("auth_token",auth_token)
        if auth_token=='':
            auth = False
        if auth_token:
            try:
                #decode
                payload=jwt.decode(auth_token,Settings.secretKey,"HS256")
                g.userid=payload['userid']
                g.username=payload['username']
            except jwt.exceptions.InvalidSignatureError as err:
                print(err)
                auth=False
        
        if auth==False:
            return render_template('login.html',message='Please login to render the service')
        
        value = func(*args, **kwargs)
        # Do something after
        return value
    return secure_login





