
import mysql.connector

def connection():
    conn = mysql.connector.connect(host="us-cdbr-iron-east-02.cleardb.net",
                            user = "b70af944e93ac1",
                            passwd= "e2aed107",
                            db = "heroku_78cf1cf050b4c37")
    c = conn.cursor()
    return c,conn
