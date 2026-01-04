import mysql.connector
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Jayant@2004",
    database="smart_schedule"
)
print("DB Connected!")
conn.close()
