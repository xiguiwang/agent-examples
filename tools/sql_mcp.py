import mysql.connector
from mysql.connector import (connection)

import json
from typing import List, Dict, Any

from mcp.server.fastmcp import FastMCP

# 创建 MCP Server
mcp = FastMCP("mcp_sql_tools")

async def database_query() -> List[Dict[str, Any]]:
    """ query database query and return formated result """
    """执行数据库查询并返回格式化结果"""
    config = {
        'user': 'root',
        'password' : 'mysql-pwd',
        'host' : '127.0.0.1',
        'port' : 9000,
        'database': 'testDB'
    }

    try:
        cnx = mysql.connector.connect(**config)
        if cnx and cnx.is_connected():
            with cnx.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Persons LIMIT 5")
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
                return rows
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return []
    finally:
        if cnx and cnx.is_connected():
            cnx.close()

# MCP工具封装函数
@mcp.tool()
async def database_query_tool() -> Dict[str, Any]:
    """ execute database query and return formated result """
    """执行数据库查询并返回格式化结果"""
    query_result = await database_query()

    return {
        "status": "success" if query_result else "empty",
        "row_count": len(query_result),
        "data": query_result,
        "timestamp": "2025-06-17T12:00:00Z"  # 添加时间戳
    }

'''
cnx = mysql.connector.connect(user=user, password=password,
    host='127.0.0.1',
    port=9000,
    database=database)
'''

if __name__ == "__main__":
    # Initialize and run the server
    #mcp.run()
    mcp.run(transport="stdio")
