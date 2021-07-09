from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash

client = MongoClient('mongodb+srv://Akash_Lo-kiB:3HvOrW2YS2O0Ksnf@cluster0.awzi6.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE&retryWrites=true&w=majority')
proj_db = client.get_database('Lo-KiB')
users_collection = proj_db.get_collection('users')
college_collection = proj_db.get_collection('college')

def register_user(mail,name,password,choice):#for registration purpose
    enct_pass = generate_password_hash(password)
    if choice == 'Student':
        users_collection.insert_one({'mail': mail, 'username': name, 'password': enct_pass, 'type': choice})
    else:
        college_collection.insert_one({'mail': mail, 'username': name, 'password': enct_pass, 'type': choice})

def get_username(username):
    return users_collection.count_documents({'username': username})

def validate_user(email):#for login authentication
    user_data = users_collection.find_one({'mail': email})
    college_data = college_collection.find_one({'mail': email})
    if user_data:
        return user_data['password'], user_data['type'] if user_data else None
    elif college_data:
        return college_data['password'], college_data['type'] if college_data else None
    else:
        return None

def get_email(email,choice):
    if choice == 'Student':
        return users_collection.count_documents({'mail':email})
    else:
        return college_collection.count_documents({'mail': email})

def update_password(user_mail, password):
    password_hash = generate_password_hash(password)
    users_collection.update_one({'mail': user_mail}, {'$set': {'password': password_hash}})
    college_collection.update_one({'mail': user_mail}, {'$set': {'password': password_hash}})
