from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import datetime
import hashlib
import secrets
import json
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
    creation_date = db.Column(db.DateTime, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)


# Check if the token is valid
def authenticate(token):
    hashed_token = hashlib.sha256(token.encode()).hexdigest()
    token = Token.query.filter_by(token=hashed_token).first()
    if not token:
        # Token not found
        return False
    elif token.revoked:
        # Token has been revoked
        return False
    elif token.expiration_date < datetime.datetime.now():
        # Token has expired
        return False
    else:
        # Token is valid
        return True


def get_token_type(token):
    hashed_token = hashlib.sha256(token.encode()).hexdigest()
    token = Token.query.filter_by(token=hashed_token).first()
    if token.type == 0:
        return 'compute'
    elif token.type == 1:
        return 'manager'
    elif token.type == 2:
        return 'user'
    else:
        return 'unknown'


@app.route('/api/token/create', methods=['POST'])
def api_token_create():
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
        return '{failure}', 400

    # Create a new Token entry in the database
    new_token = Token(token=hashed_token,
                      type=token_type_integer,
                      creation_date=datetime.now(),
                      expiration_date=expiration_date,
                      revoked=False)
    db.session.add(new_token)
    db.session.commit()

    return '{success}'


@app.route('/api/token/revoke', methods=['POST'])
def api_token_revoke():
    token_to_revoke = request.json.get('token')
    hashed_token = hashlib.sha256(token_to_revoke.encode()).hexdigest()

    # Find the token in the database
    token = Token.query.filter_by(token=hashed_token).first()
    if not token:
        return '{failure}', 404

    # Revoke the token
    token.revoked = True
    db.session.commit()

    return '{success}'


@app.route('/api/token/authenticate', methods=['POST'])
def api_token_authenticate():
    # Check if the authorization token is included in the request headers
    token = request.headers.get('Authorization')
    if not token:
        return '{failure}', 401
    print('Request has authentication token')

    # Validate the hashed authorization token against the database
    if authenticate(token):
        print('Request authenticated')
    else:
        print('Authentication failed')
        return '{failure}', 401

    token_to_authenticate = request.json.get('token')
    valid = "true" if authenticate(token_to_authenticate) else "false"
    type = get_token_type(token_to_authenticate)

    data = {
        "type": type,
        "valid": valid
    }
    return json.dumps(data)


if __name__ == '__main__':
    app.run(debug=os.environ.get('DEBUG', False))
