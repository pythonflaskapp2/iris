from os import system
from model.DatabasePool import DatabasePool
from config.Settings import Settings
import datetime
import jwt
import bcrypt
import pickle
import pandas as pd
import numpy as np




class User:
    @classmethod
    def getUsers(cls): 
        try:
            dbconn = DatabasePool.getConnection()
            cursor = dbconn.cursor(dictionary=True)
            
            sql = "select * from user"
            cursor.execute(sql)
            users =cursor.fetchall()
            return users
        finally:
            dbconn.close()
    

    @classmethod
    def getUserByUserid(cls,userid): 
        try:
            dbconn = DatabasePool.getConnection()
            cursor = dbconn.cursor(dictionary=True)
            
            sql = "select * from user where userid=%s"
            cursor.execute(sql,(userid,))
            users =cursor.fetchall()
            return users
        finally:
            dbconn.close()

            
    @classmethod
    def loginUser(cls,email,password): 
        try:
            dbconn = DatabasePool.getConnection()
            cursor = dbconn.cursor(dictionary=True)
            
            sql = "select * from user where email =%s"
            cursor.execute(sql,(email,))
            user =cursor.fetchone()

            #--jwt encode to generate a token--- 
            if user==None:
                return ""
            else:
 
                password_encode = password.encode('utf8')#convert strings to bytes
                print(password_encode)
                hashed_password = user['password'].encode('utf8')
                print(hashed_password)
                if bcrypt.checkpw(password_encode, hashed_password):
     
                    userid=user['userid']
                    username=user['username']
                    jwtToken=jwt.encode({"userid":userid,"username":username,"exp":datetime.datetime.utcnow() + datetime.timedelta(seconds=7200)},Settings.secretKey,"HS256")

                    print(jwtToken)
                    return jwtToken,username,userid
                else:
                    return "Wrong Password"

        finally:
            dbconn.close()
    
    @classmethod
    def insertUser(cls,username,email,password):
        try:


            password = password.encode('utf8') # convert strings to bytes
  
            hashed_password = bcrypt.hashpw(password,bcrypt.gensalt())
            print(hashed_password)
            dbConn=DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql="insert into user(username,email,password) values(%s,%s,%s)"
            cursor.execute(sql,(username,email,hashed_password))
            dbConn.commit()

            count=cursor.rowcount
            print(cursor.lastrowid)

            return count
        finally:
            dbConn.close()
            
    @classmethod
    def predictIris(cls,sepal_length,sepal_width,petal_length,petal_width,userid):
        try:

            data = [[sepal_length,sepal_width,petal_length,petal_width]]
            feature_names=['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
            target_name = ['Iris setosa', 'Iris versicolor','Iris virginica']
            iris_feat_df = pd.DataFrame(data=data,  columns=feature_names)
            iris_model = pickle.load(open("iris_logistic_regression.pkl","rb"))
            iris_model_pred = iris_model.predict(data)
            print("iris_model_predict",iris_model_pred)
            prediction = target_name[np.argmax(iris_model_pred)]
            pred_prob = iris_model.predict_proba(data)
            pred_prob = pred_prob[0][np.argmax(iris_model_pred)]
            
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql = "insert into irisprediction(userid,sepalLength,sepalWidth,petalLength,petalWidth,prediction) values({0}, {1}, {2}, {3}, {4}, '{5}')".format(userid,sepal_length,sepal_width,petal_length,petal_width,prediction)
            
            print (sql)
            cursor.execute(sql)
            dbConn.commit()
            
            count = cursor.rowcount
  
            sql_get = "select * from irisprediction where userid={0}".format(userid)
            cursor.execute(sql_get)

            result = cursor.fetchall()
            print ("prediction problaity", pred_prob)
            return prediction, pred_prob, result
        finally:
            dbConn.close()
    @classmethod
    def getPredictions(cls,userid):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)
            sql_get = "select * from irisprediction where userid={0} order by InsertionDate desc ".format(userid) 
            print (sql_get)
            cursor.execute(sql_get)


            result = cursor.fetchall()
            return result
        finally:
            dbConn.close()
    @classmethod
    def getPredictionsUsingEmail(cls,email):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)
            sql_get = "select * from irisprediction where userid IN (select userid from user where email='{0}') order by InsertionDate desc ".format(email) 
            print (sql_get)
            cursor.execute(sql_get)
            result = cursor.fetchall()
  
            return result
        finally:
            dbConn.close()
            
    @classmethod
    def deletePrediction(cls,pid):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)
            sql_get = "delete from irisprediction where predictionId={0}".format(pid) 
            print (sql_get)
            cursor.execute(sql_get)
            dbConn.commit()
            count = cursor.rowcount
            print (count)
            return count,pid
        finally:
            dbConn.close()
            
    @classmethod
    def verify_email(cls,email): # After user enter email for reset. verify that the email exists
        try:
            dbconn = DatabasePool.getConnection()
            cursor = dbconn.cursor(dictionary=True)
    
            sql = "select * from user where email='{0}' ".format(email)
            print(sql)
            cursor.execute(sql)
            user = cursor.fetchone()
            print(user)
            count = cursor.rowcount
            return user,count
        finally:
            dbconn.close()

    @classmethod
    def verify_username(cls,email): # After user enter email for reset. verify that the email exists
        try:
            dbconn = DatabasePool.getConnection()
            cursor = dbconn.cursor(dictionary=True)
            print(email)
            sql = "select * from user where email='{0}' ".format(email)
            print(sql)
            cursor.execute(sql)
            user = cursor.fetchall()
            print(user)
            count = cursor.rowcount
            return user
        finally:
            dbconn.close()
            
            
    @classmethod
    def updatePassword(cls,email,newpassword): # After user enter email for reset. verify that the email exists
        try:

            password = newpassword.encode('utf8') # convert strings to bytes
            print("insert",password)
            hashed_password = bcrypt.hashpw(password,bcrypt.gensalt())

            dbConn=DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql="update user set password=%s where email=%s"
            print(sql)
            cursor.execute(sql,(hashed_password,email))
            
            #cursor.execute(sql)
            dbConn.commit()

            count=cursor.rowcount
            print(cursor.lastrowid)
            return count
        finally:
            dbConn.close()
            
