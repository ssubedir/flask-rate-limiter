import random, string
import os
import sqlite3

class RateLimitSetup:
    def __init__(self):
        self.setupSqlite()

    def setupSqlite(self): #Create sqlite file
        db = sqlite3.connect("rl.db")
        c = db.cursor()

        # Token Bucket Table
        c.execute("""CREATE TABLE IF NOT EXISTS "TokenBucket" (
                                "id"	INTEGER,
                                "ip"	TEXT UNIQUE,
                                "init_request"	INTEGER,
                                "requests_available"	INTEGER,
                                PRIMARY KEY("id")
                            )""")
        # Api Key Table
        db.commit() 
        c.execute("""CREATE TABLE IF NOT EXISTS "API_KEY" (
                                "id"	INTEGER,
                                "api_key"	TEXT UNIQUE,
                                "active"	INTEGER,
                                PRIMARY KEY("id")
                            )""")
        db.commit() 
        db.close()