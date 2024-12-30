from fastapi import FastAPI
import jinja2
from pydantic import BaseModel
import uvicorn
import json
import aiohttp
import os
import re
import jwt
import uuid
import sqlite3
import psycopg2
from fastapi import FastAPI, Request, Query
import sqlite3
import uuid
from fastapi.responses import HTMLResponse
from jinja2 import Template

import datetime
app = FastAPI()





app = FastAPI()
DB_CONFIG = {
    "dbname": "ctf_service",
    "user": "ctf_user",
    "password": "ctf_password",
    "host": "db",
    "port": 5432
}

# Database Initialization
def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tokens (
        id SERIAL PRIMARY KEY,
        token TEXT,
        secret TEXT,
        companyid TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment_data (
        id SERIAL PRIMARY KEY,
        card_data TEXT,
        token TEXT,
        secret TEXT
    )
    """)
    conn.commit()
    cursor.close()
    conn.close()

init_db()

def f1a2b3c4d(e1):
    import hashlib as h
    import random as r
    j1 = e1.encode()
    k1 = h.md5(j1)
    l1 = k1.hexdigest()
    x = ''
    for i in range(len(l1)):
        x += chr(ord(l1[i]) ^ 42)
    return ''.join([chr(ord(i) ^ 42) for i in x])

#
def log_request_create_token(req: dict):
    req['quеry'] = f"INSERT INTO tokens (token, secret, companyid) VALUES ({req['token']}, {req['secret']}, {req['companyid']})"
    with open("leakage_log.log", "a") as file:
        file.write(req['quеry'] + "\n")
@app.post('/api/v1/token/create')
async def create_token(request: Request, companyid: str):
    token = str(uuid.uuid4())
    secret = f1a2b3c4d(token)
    database_request = {
        "query": """
        INSERT INTO tokens (token, secret, companyid) 
        VALUES (%s, %s, %s)
        """,
        "token": token,
        "secret": secret,
        "companyid": companyid
    }
    log_request_create_token(database_request)
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(database_request['query'], (database_request['token'], database_request['secret'], database_request['companyid']))
    conn.commit()
    cursor.close()
    conn.close()
    return {"token": token, "secret": secret}

#
def log_request_list_tokens(req: dict):
    req['query'] = "SELECT token, companyid FROM tokens"
    with open("leakage_log.log", "a") as file:
        file.write(req['query'] + "\n")
@app.get('/api/v1/token/list')
async def list_tokens(request: Request):
    database_request = {
        "query": "SELECT token, companyid FROM tokens"
    }
    log_request_list_tokens(database_request)
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(database_request['query'])
    tokens = cursor.fetchall()
    cursor.close()
    conn.close()
    return str(tokens)


#
def log_request_list_company(req: dict):
    req['query'] = f"SELECT token, companyid FROM tokens WHERE companyid='{req['company']}'"
    with open("leakage_log.log", "a") as file:
        file.write(req['query'] + "\n")
@app.post('/api/v1/token/list/company')
async def list_company_tokens(request: Request, company: str):
    database_request = {
        "query": "SELECT token, companyid FROM tokens WHERE companyid = %s",
        "company": company
    }
    log_request_list_company(database_request)
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(database_request['query'], (database_request['company'],))
    tokens = cursor.fetchall()
    cursor.close()
    conn.close()
    return str(tokens)

#
def log_request_store_payment_data(req: dict):
    req['quеry'] = f"INSERT INTO payment_data (card_data, token, secret) VALUES ({req['card_data']}, {req['token']}, {req['secret']})"
    with open("leakage_log.log", "a") as file:
        file.write(req['quеry'] + "\n")
@app.post("/api/v1/payment_data/store")
async def store_payment_data(request: Request, token: str, secret: str, card_number: str, card_secret: str):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    validation_query = "SELECT * FROM tokens WHERE token = %s AND secret = %s"
    cursor.execute(validation_query, (token, secret))
    valid = cursor.fetchone()
    if not valid:
        return {"error": "Invalid token or secret"}

    card_data = f"{card_secret}:{card_number}:{token}"
    database_request = {
        "query": """
        INSERT INTO payment_data (card_data, token, secret) 
        VALUES (%s, %s, %s)
        """,
        "card_data": card_data,
        "token": token,
        "secret": secret
    }
    log_request_store_payment_data(database_request)
    cursor.execute(database_request['query'], (database_request['card_data'], database_request['token'], database_request['secret']))
    conn.commit()
    cursor.close()
    conn.close()
    return {"success": True}

def log_request_get_payment_data(req: dict):
    req['quеry'] = f"SELECT card_data FROM payment_data WHERE token='{req['token']}' AND secret='{req['secret']}'"
    with open("leakage_log.log", "a") as file:
        file.write(req['quеry'] + "\n")
@app.get("/api/v1/payment_data/get")
async def get_payment_data(request: Request, token: str, secret: str):
    database_request = {
        "query": "SELECT card_data FROM payment_data WHERE token = %s AND secret = %s",
        "token": token,
        "secret": secret
    }
    log_request_get_payment_data(database_request)
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(database_request['query'], (database_request['token'], database_request['secret']))
    payment_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"payment_data": [data[0] for data in payment_data]}



def verify_auth_and_do_some_debug_loggin_stuff(data, token):    
    print(data)
    try:
        token = jwt.decode(token, key='godmod_rulezz', algorithms=['HS256', ])
        if data.get("log_request", False):
            data['addr'] = token['dept']
            data['login'] = token['login']
            data['timestamp'] = datetime.datetime.now().timestamp()
            data['service'] = "remote_access"
        with open("access_log.txt", "a") as logfile:
            logfile.write(json.dumps(data) + ",\n")
        print(data)
    except KeyboardInterrupt as es:
        print(es)
        print("verify failed")
        return False
    return True

def match_office(data):
    office_mapping = {
        #domain controller which allows connections only from checkers
        "nyc_office": "godmode.free.beeceptor.com",
    }
    return office_mapping[data]

class CreateSessionStruct(BaseModel):
    token: str
    conn_data:dict

async def authorize_domain_controller(url: str, token: str):
    async with aiohttp.ClientSession() as sess:
        res = await sess.get("http://" +url + "/authorize", params={"token": token})
        
        print(await res.text())
        return await res.json()

@app.post("/api/v1/command/exec")
async def create_virtual_desktop(req: CreateSessionStruct):
    data = req.conn_data
    conn_status = ""
    
    print(req.token)

    if data['addr'] in ['nyc_office', "msk_office"]:
        data['addr'] = match_office(data['addr'])
        if verify_auth_and_do_some_debug_loggin_stuff(data=data, token=req.token):
            is_domain_controller_authorized = await authorize_domain_controller(data['addr'], req.token)
            if not is_domain_controller_authorized['allow']:
                return "not authorized"
            conn_status = "session opened on mapped address"
    else:
        
        print(data)
        if re.search("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",data['addr']):
            conn_status = "illegal connection source"
            return conn_status
        conn_status = "connection opened on non-mapped address"
    print(conn_status)
    cmd_stdout = os.popen(f"tail -100 {data['filename']}").read()
    return cmd_stdout

    return conn_status



@app.get("/api/v1/remote/token")
async def gen_token(login, password,dept):
    payload_data = {
    "login": login,
    "pass": password,
    "dept": dept
    }
    token = jwt.encode(
    payload=payload_data,
    key="godmod_rulezz"
)
    return token.encode()

# if __name__ == "__main__":
#     uvicorn.run(app)