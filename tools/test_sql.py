import mysql.connector
from mysql.connector import (connection)

user='root'
password='mysql-pwd'
database='testDB'

cnx = mysql.connector.connect(user=user, password=password,
                                 host='127.0.0.1',
                                 port=3306,
                                 database=database)
'''
cnx = connection.MySQLConnection(user=user, password=password,
                                 host='127.0.0.1',
                                 port=9000,
                                 database=database)
'''
if cnx and cnx.is_connected():
    with cnx.cursor(dictionary=True) as cursor:
        result = cursor.execute("SELECT * FROM Persons_InfoTb LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    cnx.close()
else:
    print("Could not connect")

#cnx.close()
