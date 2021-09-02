from mysql.connector import pooling 
from config.Settings import Settings
class DatabasePool:

    #connection_pool = pooling.MySQLConnectionPool(
     #                         pool_name="ws_pool",
      #                       pool_size=1,
       #                      host=Settings.host,
        #                     database=Settings.database,
         #                     user=Settings.user,
          #             password=Settings.password)
          
    connection_pool = pooling.MySQLConnectionPool(
                    pool_name="ws_pool",
                    pool_size=5,
                    host='localhost',
                    database='iris-db',
                    user='root',
            password= 'password')
 
    @classmethod
    def getConnection(cls): 
        dbConn = cls.connection_pool.get_connection()
        return dbConn
