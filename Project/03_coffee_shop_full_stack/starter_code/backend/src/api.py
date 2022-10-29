from crypt import methods
import os
from turtle import title
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
app.config['JSON_SORT_KEYS'] = False

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
@app.route('/', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    print(drinks)

    try:
        short_drinks = [drink.short() for drink in drinks]

    except:
        abort(404)

    print(short_drinks)
    return jsonify({
        'success': True,
        'drinks': short_drinks,
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(token):
    drinks = Drink.query.all()
    print(drinks)

    try:
        long_drinks = [drink.long() for drink in drinks]
        print(long_drinks)

        if len(long_drinks) == 0:
            abort(404)

    except:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': long_drinks,
    }), 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(token):
    body = request.get_json()

    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)
    print(new_title)
    print(new_recipe)

    new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))

    new_drink.insert()
    print("success")

    return jsonify({
        'success': True,
        'drinks': new_drink.long(),
    }), 200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(token,drink_id):
    body = request.get_json()

    find_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if find_drink is None:
        print("I am a 404")
        print(find_drink)
        abort(404)  
    else:
        if "title" in body:
            find_drink.title = body.get("title")

        if "recipe" in body:
            find_drink.recipe = json.dumps(body.get("recipe"))

        find_drink.update()

    return jsonify({
        'success': True,
        'drinks': find_drink.long(),
    }), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token,drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()
    
        return jsonify({
            'success': True,
            'drinks': drink_id,
        }), 200
    except:
        abort(404)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'bad request'
    }), 400

@app.errorhandler(401)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'unauthorized'
    }), 401

@app.errorhandler(403)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": 'forbidden'
    }), 403


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": 'resource not found'
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
