import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

#db_drop_and_create_all()
print('Backend server restarted')

# ROUTES


@app.route('/drinks', methods=(['GET']))
def get_drinks():
    drinks = Drink.query.all()
    if len(drinks) is 0:
        abort(404)
    formatted_drinks = [drink.short() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


@app.route('/drinks-detail', methods=(['GET']))
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail(permissions):
    drinks = Drink.query.all()
    if len(drinks) is 0:
        abort(404)

    formatted_drinks = [drink.long() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


@app.route('/drinks', methods=(['POST']))
@requires_auth(permission='post:drinks')
def post_drink(payload):
    form = request.get_json()
    title = form['title']
    recipe = str(form['recipe']).replace('\'','"')
    print('NEW DRINK:',title,recipe)
    drink = Drink(title=title, recipe=recipe)
    drink.insert()

    return jsonify({
        'success': True
    })


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


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "Not Found",
                    "error_message": error
    }), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "Unauthorized",
                    "error_message": error
    }), 401


@app.errorhandler(AuthError)
def handle_auth_error(exception):
    print('*** AUTH ERROR ***')
    return jsonify({
        'success': False,
        'error': exception.status_code,
        'error_message': exception.error
    }), exception.status_code
