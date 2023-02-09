from fastapi import FastAPI,Form
import pymongo
from pydantic import BaseModel
from bson.objectid import ObjectId
from typing import Optional
from fastapi.responses import HTMLResponse
from jinja2 import Environment,FileSystemLoader

app = FastAPI()
my_client = pymongo.MongoClient('localhost',27017)


my_db = my_client['bio']
my_collec = my_db['users']

load = Environment(loader=FileSystemLoader('templates'))

@app.get('/')
async def home():
    template = load.get_template('base.html')
    user_data = []
    for user in my_collec.find():
        user_data.append(user)
    msg = { 
        'type' : 'Greetings',
        'description' : 'Heyy User..Welcome to Ikonz',
        'users' : user_data
    }
    html = template.render(msg)
    return HTMLResponse(content=html)

def get_data(db,collec):
    data = []
    my_db = my_client[db]
    my_collec = my_db[collec]
    for actor in my_collec.find():
        data.append(
            {
                'id': str(actor["_id"]),
                'name' : actor['name'],
                'email' : actor['email'],
                'phone' : actor['phone'],
            }
        )
    return data

@app.get('/get_all_accounts/')
async def get_all():
    actors = get_data('bio','users')
    return {'all_user_bio':actors}

@app.get('/get-by-id/{_id}')
async def get_by_id(_id: str):
    data = []
    for actor in my_collec.find():
        if str(actor['_id'])==_id:
            data.append({'name' : actor['name'],
                    'email' : actor['email'],
                    'phone' : actor['phone'],})
    return {f'ObjectId({_id})':data}

@app.get('/get-by-query')
async def get_by_query(search: str):
    new_db = {}
    for item in my_collec.find():
        for key,val in dict(item).items():
            if search == val or str(item['_id'])==search or search == str(item['phone']):
                new_db['name'] = item['name']
                new_db['email'] = item['email']
                new_db['phone'] = item['phone']
    return {'response' : new_db}

class User(BaseModel):
    name : Optional[str]=Form(...)
    email : Optional[str]=Form(...)
    phone : Optional[str]=Form(...)

@app.post('/create-user')
async def create_actor(user: User):
    new_db = {}
    new_db['name'] = user.name
    new_db['email'] = user.email
    new_db['phone'] = user.phone

    my_collec.insert_one(new_db)
    return {'response' : f'{user.name} has loaded successfully in data'}

@app.post('/update-user/{_id}')
async def update_user(user: User,_id):
    query = {'_id':ObjectId(_id)}
    check = {key:val for key,val in user if val!=None}
    for i in check:
        newvalues = { "$set": {i : check[i]} }
        my_collec.update_one(query,newvalues) 
        print(i,check[i])
    return {'response' : 'details updated successfully'}
