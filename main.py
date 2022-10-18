from ast import Or
import json
import psycopg2
from flask import Flask, request, jsonify

from db import *
from user import Users
from org import Organizations

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://sarahroy@localhost:5432/alchemy"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app, db)

def create_all():
  with app.app_context():
    print("Creating tables...")
    db.create_all()
    print("All done!")

@app.route('/user/add', methods=['POST'] )
def user_add():
  post_data = request.json
  
  if not post_data:
    post_data = request.post
  
  first_name = post_data.get('first_name')
  last_name = post_data.get('last_name')
  email = post_data.get('email')
  phone = post_data.get('phone')
  city = post_data.get('city')
  state = post_data.get('state')
  org_id = post_data.get('org_id')
  active = post_data.get('active')

  add_user(first_name, last_name, email, phone, city, state, org_id, active)

  return jsonify("User created"), 201

  

def add_user(first_name, last_name, email, phone, city, state, org_id, active): 
  new_user = Users(first_name, last_name, email, phone, city, state, org_id, active)
  
  db.session.add(new_user)
  db.session.commit()

@app.route('/org/add', methods=['POST'] )
def org_add():
    post_data = request.json
    if not post_data:
        post_data = request.form
    name = post_data.get('name')
    phone = post_data.get('phone')
    city = post_data.get('city')
    state = post_data.get('state')
    active = post_data.get('active')

    add_org(name, phone, city, state, active)

    return jsonify("Org created"), 201

def add_org(name, phone, city, state, active):
  new_org = Organizations(name, phone, city, state, active)
  db.session.add(new_org)
  db.session.commit()

@app.route('/user_by_id/get/<user_id>', methods=['GET'] )
def get_user_by_id(user_id):
  user = db.session.query(Users).filter(Users.user_id == user_id).first()
  
  if user:
    new_user = {
      'user_id': user.user_id,
      'first_name': user.first_name,
      'last_name': user.last_name,
      'email': user.email,
      'phone': user.phone,
      'city': user.city,
      'state': user.state,
      'organization': {
        'org_id': user.org.org_id,
        'name': user.org.name,
        'phone': user.org.phone,
        'city': user.org.city,
        'state': user.org.state
      },
      'active': user.active
    }

  return jsonify(new_user), 200

@app.route('/org_by_id/<org_id>', methods=['GET'] )
def get_org_by_id(org_id):
  results = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()

  if results:
    org = {
      'org_id': results.org_id,
      'name': results.name,
      'phone': results.phone,
      'city': results.city,
      'state': results.state,
      'active': results.active,
    },

  return jsonify(org), 200

@app.route('/users/get', methods=['GET'] )
def get_all_active_users():
  users = db.session.query(Users).filter(Users.active == True).all()
  users_list = []

  for user in users:
    new_user = {
      'user_id': user.user_id,
      'first_name': user.first_name,
      'last_name': user.last_name,
      'email': user.email,
      'phone': user.phone,
      'city': user.city,
      'state': user.state,
      'organization': {
        'org_id': user.org.org_id,
        'name': user.org.name,
        'phone': user.org.phone,
        'city': user.org.city,
        'state': user.org.state
      },
      'active': user.active
    }

    users_list.append(new_user)

  return jsonify(users_list), 200

@app.route('/org/get', methods=['GET'] )
def get_active_orgs():
  orgs = db.session.query(Organizations).filter(Organizations.active == True).all()
  orgs_list = []


  for org in orgs:
    new_org = {
      'org_id': org.org_id,
      'name': org.name,
      'phone': org.phone,
      'city': org.city,
      'state': org.state,
      'active': org.active
    }

    orgs_list.append(new_org)

  return jsonify(orgs_list), 200

@app.route('/user/update/<user_id>', methods=['POST', 'PUT'] )
def edit_user(user_id, first_name = None, last_name = None, email = None, password = None, city = None, state = None, active = None):
  user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

  if not user_record:
    return('User not found'), 404

  if request:
    post_data = request.json
    first_name = post_data.get('first_name')
    last_name = post_data.get('last_name')
    email = post_data.get('email')
    password = post_data.get('password')
    city = post_data.get('city')
    state = post_data.get('state')
    active = post_data.get('active')
  
  if first_name:
    user_record.first_name = first_name
  if last_name:
    user_record.last_name = last_name
  if email:
    user_record.email = email
  if password:
    user_record.password = password
  if city:
    user_record.city = city
  if state:
    user_record.state = state
  if active:
    user_record.active = active
  
  db.session.commit()

  return jsonify('User Updated'), 201

@app.route('/org/update/<org_id>', methods=['POST', 'PUT'] )
def edit_org(org_id, name = None, phone=None, city = None, state = None, active = None):
  org_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()

  if not org_record:
    return('User not found'), 404

  if request:
    post_data = request.json
    name = post_data.get('name')
    phone = post_data.get('phone')
    city = post_data.get('city')
    state = post_data.get('state')
    active = post_data.get('active')
    
  if name:
    org_record.name = name
  if phone:
    org_record.phone = phone
  if city:
    org_record.city = city
  if state:
    org_record.state = state
  if active:
    org_record.active = active
  
  db.session.commit()

  return jsonify('Organization Updated'), 201

@app.route('/user/activate/<user_id>', methods=['GET'] )
def user_activate(user_id):
  results = db.session.query(Users).filter(Users.user_id == user_id).first()
  results.active=True
  db.session.commit()
  return jsonify('User Activated'), 200

@app.route('/org/activate/<org_id>', methods=['GET'] )
def org_activate(org_id):
  results = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
  results.active=True
  db.session.commit()
  return jsonify('Organization Activated'), 200

@app.route('/user/deactivate/<user_id>', methods=['GET'] )
def user_deactivate(user_id):
  results = db.session.query(Users).filter(Users.user_id == user_id).first()
  results.active=False
  db.session.commit()
  return jsonify('User Deactivated'), 200

@app.route('/org/deactivate/<org_id>', methods=['GET'] )
def org_deactivate(org_id):
  results = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
  results.active=False
  db.session.commit()
  return jsonify('Organization Deactivated'), 200

@app.route('/user/delete/<user_id>', methods=['DELETE'] )
def user_delete(user_id):
  results = db.session.query(Users).filter(Users.user_id == user_id).first()
  db.session.delete(results)
  db.session.commit()
  return jsonify('User Deleted'), 200

@app.route('/org/delete/<org_id>', methods=['DELETE'] )
def org_delete(org_id):
  results = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
  db.session.delete(results)
  db.session.commit()
  return jsonify('Organization Deleted'), 200

if __name__ == '__main__':
  create_all()
  app.run(host='0.0.0.0', port="4000")