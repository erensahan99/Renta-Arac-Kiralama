
import mysql.connector

def connection():
    conn = mysql.connector.connect(host="us-cdbr-iron-east-02.cleardb.net",
                            user = "be03d4522f4269",
                            passwd= "28171904",
                            db = "heroku_6b66bc0805cf409")
    c = conn.cursor()
    return c,conn
