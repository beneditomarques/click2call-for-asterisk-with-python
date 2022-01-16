from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import models
from asterisk.ami import AMIClient, SimpleAction
import os
import redis
import json
import uuid
import time
import random

app = FastAPI()   

def get_redis_client():
    redis_host = "redis"
    redis_port = 6379
    redis_password = ""   
    return redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

def callback_response(response):    
    print(response)    
    
def event_listener(event,**kwargs): 
    r = get_redis_client()
    print(event.keys)    
    actionid = event.keys['ActionID']
    actionid = actionid+str(time.time())+str(random.randint(0,1000))    
    r.set(str(actionid), json.dumps([event.keys]))


@app.post("/click2call", tags=["click2call"])
def click2call(body: models.Click2call, credentials: HTTPBasicCredentials = Depends(HTTPBasic())):            
    username = credentials.username
    password = credentials.password
    data     = body.dict()
    src      = data['src']
    dst      = data['dst']
    context  = data['context']

    if username != os.environ['HTTP_AUTH_USER'] or password != os.environ['HTTP_AUTH_PASSWORD']:    
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    client = AMIClient(address=os.environ['ASTERISK_IP'],port=int(os.environ['ASTERISK_AMI_PORT']))
    client.login(username=os.environ['ASTERISK_AMI_USER'],secret=os.environ['ASTERISK_AMI_PASSWORD']) 
    action = SimpleAction(
        'Originate',
        Channel='SIP/'+str(src),
        Exten=str(dst),
        Priority=1,
        Context=str(context),
        CallerID='Python app',
    )    
    future = client.send_action(action,callback=callback_response)
    reponse = future.response
    client.logoff()    
    return reponse
    
    
    
@app.get("/get_extensions", tags=["Listextensions"])
def get_extensions(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    username = credentials.username
    password = credentials.password

    if username != 'superuser' or password != 'supersecret':    
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )        
    client = AMIClient(address=os.environ['ASTERISK_IP'],port=int(os.environ['ASTERISK_AMI_PORT']))
    client.login(username=os.environ['ASTERISK_AMI_USER'],secret=os.environ['ASTERISK_AMI_PASSWORD']) 
    actionid = uuid.uuid1()
    action = SimpleAction(
        'SIPpeerstatus',
        ActionID=actionid
    )    
    client.send_action(action,callback=callback_response)            
    client.add_event_listener(
        event_listener,
        white_list='PeerStatus'
    )
    client.logoff()    
    time.sleep(1)
    r = get_redis_client()
    keys = r.keys(str(actionid)+'*')
    result = []
    for key in keys:
        result.append(json.loads(r.get(key)))
        r.delete(key) 
    r.flushall()   
    r.close()
    return result
    

