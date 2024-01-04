from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import hashlib
import secrets
import os

# Initialize Flask
app = Flask(__name__)

# Database config
DATABASE_HOST = os.environ.get('DB_HOST')
DATABASE_NAME = os.environ.get('DB_NAME')
DATABASE_USER = os.environ.get('DB_USER')
DATABASE_PASS = os.environ.get('DB_PASS')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(DATABASE_USER, DATABASE_PASS, DATABASE_HOST, DATABASE_NAME)

db = SQLAlchemy(app)


# Represents the entries in the database
class Token(db.Model):
    __tablename__ = 'token'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(48), unique=True, nullable=False)
    type = db.Column(db.Integer)  # 0 = compute, 1 = manager, 2 = user
    expiration_date = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)


# Authenticate the request
def authenticate(request, type='any'):
    token = request.headers.get('Authorization')
    hashed_token = hashlib.sha256(token.encode()).hexdigest()
    token = Token.query.filter_by(token=hashed_token).first()
    if not token:
        # Token not found
        return False
    elif token.revoked:
        # Token has been revoked
        return False
    elif token.expiration_date < datetime.now():
        # Token has expired
        return False
    else:
        # Token is valid
        return True


@app.route('/api/common/version', methods=['POST'])
def api_common_version():
    with app.app_context():
        if not authenticate(request):
            return jsonify({'error': True}), 401
    return jsonify({'version': os.environ.get('STARGAZER_VERSION')}), 200


@app.route('/api/common/type', methods=['POST'])
def api_common_type():
    with app.app_context():
        if not authenticate(request):
            return jsonify({'error': True}), 401
    return jsonify({'version': os.environ.get('STARGAZER_TYPE')}), 200


@app.route('/api/token/create', methods=['POST'])
def api_token_create():
    # Check for required fields
    if not request.json:
        return jsonify({'error': True}), 400
    elif not request.json.get('type'):
        return jsonify({'error': True}), 400
    elif not request.json.get('expiration_date'):
        return jsonify({'error': True}), 400

    # Check for correct data types
    if not isinstance(request.json.get('type'), str):
        return jsonify({'error': True}), 400
    elif not isinstance(request.json.get('expiration_date'), str):
        return jsonify({'error': True}), 400

    # Check for valid token length
    if len(request.json.get('token')) != 48:
        return jsonify({'error': True}), 400

    # Authenticate the request
    if not authenticate(request, 'user'):
        return jsonify({'error': True}), 401

    # Extract information from the request
    expiration_date = request.json.get('expiration_date')
    token_to_create = secrets.token.urlsafe(48)
    hashed_token = hashlib.sha256(token_to_create.encode()).hexdigest()

    # Convert the token type string to an integer
    if request.json.get('type') == 'compute':
        token_type_integer = 0
    elif request.json.get('type') == 'manager':
        token_type_integer = 1
    elif request.json.get('type') == 'user':
        token_type_integer = 2
    else:
        return jsonify({'error': True}), 400

    # Create a new Token entry in the database
    new_token = Token(token=hashed_token,
                      type=token_type_integer,
                      creation_date=datetime.now(),
                      expiration_date=expiration_date,
                      revoked=False)
    db.session.add(new_token)
    db.session.commit()

    return jsonify({"token": token_to_create}), 201


@app.route('/api/token/revoke', methods=['POST'])
def api_token_revoke():
    # Check for required fields
    if not request.json:
        return jsonify({'error': True}), 400
    elif not request.json.get('token'):
        return jsonify({'error': True}), 400

    # Check for correct data types
    if not isinstance(request.json.get('token'), str):
        return jsonify({'error': True}), 400

    # Check for valid token length
    if len(request.json.get('token')) != 48:
        return jsonify({'error': True}), 400

    # Authenticate the request
    if not authenticate(request, 'user'):
        return jsonify({'error': True}), 401

    # Extract information from the request
    token_to_revoke = request.json.get('token')
    hashed_token = hashlib.sha256(token_to_revoke.encode()).hexdigest()

    # Find the token in the database
    token = Token.query.filter_by(token=hashed_token).first()
    if not token:
        return jsonify({'error': True}), 400

    # Revoke the token
    token.revoked = True
    db.session.commit()

    return jsonify({'success': True}), 200


@app.route('/api/token/authenticate', methods=['POST'])
def api_token_authenticate():
    # Check for required fields
    if not request.json:
        return jsonify({'error': True}), 400
    elif not request.json.get('token'):
        return jsonify({'error': True}), 400

    # Check for correct data types
    if not isinstance(request.json.get('token'), str):
        return jsonify({'error': True}), 400

    # Check for valid token length
    if len(request.json.get('token')) != 48:
        return jsonify({'error': True}), 400

    # Authenticate the request
    if not authenticate(request, 'user'):
        return jsonify({'error': True}), 401

    # Extract information from the request
    token_to_authenticate = request.json.get('token')

    # Check for valid token length
    if len(token_to_authenticate) != 48:
        return jsonify({'error': True}), 400

    # Check if the token is valid
    valid = "true" if authenticate(token_to_authenticate) else "false"

    # Look up its type in the database
    hashed_token = hashlib.sha256(token_to_authenticate.encode()).hexdigest()
    token = Token.query.filter_by(token=hashed_token).first()
    if token.type == 0:
        type = 'compute'
    elif token.type == 1:
        type = 'manager'
    elif token.type == 2:
        type = 'user'
    else:
        return jsonify({'error': True}), 400

    # Response
    return jsonify({"type": type, "valid": valid}), 200


if __name__ == '__main__':
    app.run(debug=os.environ.get('DEBUG', False))
