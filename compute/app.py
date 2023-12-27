from flask import Flask, request, send_file
from flask_sqlalchemy import SQLAlchemy
import hashlib
import os

# Initialize Flask
app = Flask(__name__)

# Database config
DATABASE_HOST = os.environ.get('DB_HOST')
DATABASE_NAME = os.environ.get('DB_NAME')
DATABASE_USER = os.environ.get('DB_USER')
DATABASE_PASS = os.environ.get('DB_PASS')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + DATABASE_USER + ':' + DATABASE_PASS + '@' + DATABASE_HOST + '/' + DATABASE_NAME

db = SQLAlchemy(app)


# Represents the entries in the database
class Token(db.Model):
    __tablename__ = 'token'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(48), unique=True, nullable=False)


@app.route('/api/version')
def generate_step():
    print('Request received')

    # Check if the authorization token is included in the request headers
    token = request.headers.get('Authorization')
    if not token:
        return 'Unauthorized', 401
    print('Request has authentication token')

    # Validate the hashed authorization token against the database
    hashed_token = hashlib.sha256(token.encode()).hexdigest()
    if not Token.query.filter_by(token=hashed_token).first():
        print('Authentication failed')
        return 'Unauthorized', 401
    print('Request authenticated')

    return version


if __name__ == '__main__':
    app.run(debug=os.environ.get('DEBUG', False))