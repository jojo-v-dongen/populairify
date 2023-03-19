from mysql.connector import pooling

DB_CONFIG = {
    'host': '',
    'user': '',
    'password': '',
    'database': ''
}

connection_pool = pooling.MySQLConnectionPool(pool_name="my_pool", pool_size=10, **DB_CONFIG)