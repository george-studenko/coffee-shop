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
    formatted_drinks = []
    if len(drinks) > 0:
        formatted_drinks = [drink.short() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })



@app.route('/drinks-detail', methods=(['GET']))
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail(permissions):
    drinks = Drink.query.all()
    formatted_drinks = []

    if len(drinks) is 0:
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
    recipe = '['+ str(form['recipe']).replace('\'','"') + ']'
    drink = Drink(title=title, recipe=recipe)
    drink.insert()

    return jsonify({
        'success': True
    })


@app.route('/drinks/<int:id>', methods=(['PATCH']))
@requires_auth(permission='patch:drinks')
def update_drink(payload, id):
    form = request.get_json()

    drink = Drink.query.get(id)
    print('DRINK IS:',drink)
    if drink is None:
        abort(404)

    if 'title' in form.keys():
        drink.title = form['title']

    if 'recipe' in form.keys():
        drink.recipe = '['+ str(form['recipe']).replace('\'','"') + ']'

    drink.update()
    drinks_formatted = []
    drinks_formatted.append(drink.long())
    return jsonify({
        'success': True,
        'drinks': drinks_formatted
    })


@app.route('/drinks/<int:id>', methods=(['DELETE']))
@requires_auth(permission='delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    drink.delete()
    return jsonify({
        'success': True,
        'delete': id
    })


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
    print('*** AUTH ERROR ***', exception)
    return jsonify({
        'success': False,
        'error': exception.status_code,
        'error_message': exception.error
    }), exception.status_code
