from model.DatabasePool import DatabasePool
from config.Settings import Settings
import datetime
import jwt

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
            users =cursor.fetchone()
            print("Come here")
            print(users)
            #--jwt encode to generate a token--- 
            if users == None:
               return  ""
            else:
                print("users is there")
                role = users['role']
                userid = users['userid']
                username = users['username']
                jwtToken = jwt.encode({"role":role,"userid":userid,"username":username, "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=7200)},Settings.secretKey)
                print(jwtToken)
                return jwtToken,username
            
            return users
        finally:
            dbconn.close()
            

            


