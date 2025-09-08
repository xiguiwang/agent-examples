import mysql.connector
from mysql.connector import (connection)

user='root'
password='mysql-pwd'
#database='testDB'
database='foodDB'

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
        insert_query = "INSERT INTO food_InfoTb (foodName, foodType, PicUrl) \
                VALUES (%s, %s, %s)"
        food_data = (
                '白菜',  # foodName
                '蔬菜',  # foodType
                'https://example.com/apple.jpg'  # PicUrl
                )
        result = cursor.execute(insert_query, food_data)
        #result = cursor.execute("INSERT INTO food_InfoTb(foodName, foodType, PicUrl) VALUES ('土豆', '蔬菜', 'https://example.com/apple.jpg')")
        # 提交事务
        cnx.commit()
            
        print("数据插入成功！")
        #rows = cursor.fetchall()
        #for row in rows:
        #    print(row)
    cnx.close()
else:
    print("Could not connect")

#cnx.close()
