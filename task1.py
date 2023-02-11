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

def get_data():
    data = []
    for user in my_collec.find():
        data.append(
            {
                'id': str(user["_id"]),
                'name' : user['name'],
                'email' : user['email'],
                'phone' : user['phone'],
            }
        )
    return data

@app.get('/get_all_accounts/')
async def get_all():
    users = get_data()
    return {'all_user_bio' : users}

@app.get('/get-by-id/{_id}')
async def get_by_id(_id: str):
    user = my_collec.find_one({'_id':ObjectId(_id)})
    unpacked_data = {
                'id': str(user["_id"]),
                'name' : user['name'],
                'email' : user['email'],
                'phone' : user['phone'],
            }
    return {'response' : unpacked_data}

@app.get('/get-by-query')
async def get_by_query(search: str):
    unpacked_data = {}
    for item in my_collec.find():
        if search in dict(item).values() or search == str(item['_id']):
            unpacked_data = {
                'id': str(item['_id']),
                'name' : item['name'],
                'email' : item['email'],
                'phone' : item['phone'],
            }
    return {'response' : unpacked_data}

class User(BaseModel):
    name : Optional[str]
    email : Optional[str]
    phone : Optional[str]

@app.post('/create-user')
async def create_actor(user: User):
    new_db = {}
    new_db['name'] = user.name
    new_db['email'] = user.email
    new_db['phone'] = user.phone

    my_collec.insert_one(new_db)
    return {'response' : f'{user.name} has loaded successfully in data'}

@app.post('/update-user')
async def update_user(user: User,_id):
    query = {'_id':ObjectId(_id)}
    check = {key:val for key,val in user if val!=None}
    for i in check:
        newvalues = { "$set": {i : check[i]} }
        my_collec.update_one(query,newvalues)
    return {'response' : 'details updated successfully'}

@app.delete('/delete-user')
async def delete_user(_id):
    query = {'_id':ObjectId(_id)}
    my_collec.find_one_and_delete(query)
    return {'response' : 'user deleted succeccfully'}
