from werkzeug.wrappers import Request, Response
from werkzeug.datastructures import Headers
from datetime import datetime
import os
import sqlite3
import calendar
import time
import json


# Rate Limit Middleware
class Middleware():
     
    def __init__(self, app):
        self.app = app
        # Rate limit reset duration and rate
        self.duration = int (os.getenv('DEFAULT_DURATION')) 
        self.rate = int (os.getenv('DEFAULT_RATE'))

    def __call__(self, environ, start_response):
        request = Request(environ) 
        key = request.headers.get("auth") # get key from request header
        if key!=None: # api key based rate limiting
            if self.Api_Rate_limiter(key): # validate api key
                 return self.app(environ, start_response)
            else: # validate failed fall back to ip based rate limiting
                if self.Ip_Rate_limiter(request): 
                    return self.app(environ, start_response)
                else:
                    h = Headers()
                    h.add("content-type","application/json")
                    # Respond Message
                    r = {
                        "status":429,
                        "error":"Too Many Requests",
                        "message": "Api requests limit reached. You are able to make {} requests per every {} seconds.".format(self.rate,self.duration)
                        }
                    res = Response(json.dumps(r), status=429 ,headers=h )
                    return res(environ, start_response)

        else: # defaults to ip based rate limiting if api key validation fails or not provided
            if self.Ip_Rate_limiter(request): 
                return self.app(environ, start_response)
            else:
                h = Headers()
                h.add("content-type","application/json")
                # Respond Message
                r = {
                    "status":429,
                    "error":"Too Many Requests",
                    "message": "Api requests limit reached. You are able to make {} requests per every {} seconds.".format(self.rate,self.duration)
                    }
                res = Response(json.dumps(r), status=429 ,headers=h )
                return res(environ, start_response)
        
    #ip based rate limiter
    def Ip_Rate_limiter(self,request):
        conn = sqlite3.connect("rl.db")
        c = conn.cursor()
        c.execute("SELECT * FROM TokenBucket WHERE ip=?",(request.remote_addr,))
        fetch = c.fetchall()
        conn.commit()
        
        ts = calendar.timegm(time.gmtime())

        if(len(fetch)== 0): # first request
            c.execute("INSERT INTO TokenBucket (ip,init_request,requests_available) VALUES (?,?,?)",(request.remote_addr,ts,self.rate-1))
            conn.commit()
            conn.close()
            print("First Request")
            return True
        else:

            requests_available = fetch[0][3] # limit available
            init_request = fetch[0][2] # time stamp
            
            

            if requests_available !=0:
                c.execute("UPDATE TokenBucket SET requests_available = ? WHERE ip=?",(requests_available - 1,request.remote_addr)) # update
                conn.commit()

                if self.checkDur(init_request).total_seconds() > self.duration: # reset timer
                    c.execute("UPDATE TokenBucket SET requests_available = ? WHERE ip=?",(self.rate-1,request.remote_addr)) # update
                    conn.commit()
                conn.close()
                print(requests_available-1)
                print(init_request)
                return True
            else:
                if self.checkDur(init_request).total_seconds() > self.duration: # reset timer
                    c.execute("UPDATE TokenBucket SET init_request = ?, requests_available = ? WHERE ip=?",(ts,self.rate-1,request.remote_addr)) # update
                    conn.commit()
                    return True
                conn.close()
                return False

    #api key based rate limiter           
    def Api_Rate_limiter(self,key):
        conn = sqlite3.connect("rl.db")
        c = conn.cursor()
        c.execute("SELECT * FROM API_KEY WHERE api_key=?",(key,))
        fetch = c.fetchall()
        conn.commit()

        if len(fetch) == 1: # key exists in db
            active = fetch[0][2]

            if active == 1:
                conn.close()
                return True
            else:
                conn.close()
                return False

        else:
            conn.close()
            return False

    # check duration between now anf the initial request
    def checkDur(self,timestamp):
        now = datetime.now()
        then = datetime.fromtimestamp(timestamp)
        dur =  now - then
        return dur




        


