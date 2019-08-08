
import mysql.connector

def connection():
    conn = mysql.connector.connect(host="localhost",
                            user = "root",
                            passwd= "root",
                            db = "renta")
    c = conn.cursor()
    return c,conn
