from flask import Flask, request, jsonify
import requests
import os

# Initialize Flask
app = Flask(__name__)


def authenticate(request, type='any'):
    # Convert type to integer
    if type == 'compute':
        type = 0
    elif type == 'manager':
        type = 1
    elif type == 'user':
        type = 2
    elif type == 'any':
        type = 3
    else:
        return False

    # Check if the authorization token is included in the request headers
    token = request.headers.get('Authorization')
    if not token:
        return False

    # Request authentication on the server
    response = requests.post('{}/api/token/authenticate'.format(os.environ.get('AUTH_ENDPOINT')),
                             json={'token': token},
                             timeout=5)

    # Check if the token is valid
    if not response.json().get('valid') == 'true':
        return False

    # Check if the token is of requested type
    if type != 3 and not response.json().get('type') == type:
        return False

    # Request authenticated
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


@app.route('/api/compute/update', methods=['POST'])
def api_compute_update():
    if not authenticate(request, 'manager'):
        return 'Unauthorized', 401
    return response


@app.route('/api/compute/configure', methods=['POST'])
def api_compute_configure():
    if not authenticate(request, 'manager'):
        return 'Unauthorized', 401
    return response


@app.route('/api/compute/assign', methods=['POST'])
def api_compute_assign():
    if not authenticate(request, 'manager'):
        return 'Unauthorized', 401
    return response


@app.route('/api/compute/potential/gravity', methods=['POST'])
def api_compute_potential_gravity():
    if not authenticate(request, 'manager'):
        return 'Unauthorized', 401
    return response


@app.route('/api/compute/potential/electrostatic', methods=['POST'])
def api_compute_potential_electrostatic():
    if not authenticate(request, 'manager'):
        return 'Unauthorized', 401
    return response


@app.route('/api/compute/force/gravity', methods=['POST'])
def api_compute_force_gravity():
    if not authenticate(request, 'manager'):
        return 'Unauthorized', 401
    return response


@app.route('/api/compute/force/electrostatic', methods=['POST'])
def api_compute_force_electrostatic():
    if not authenticate(request, 'manager'):
        return 'Unauthorized', 401
    return response


@app.route('/api/compute/integrate', methods=['POST'])
def api_compute_integrate():
    if not authenticate(request, 'manager'):
        return 'Unauthorized', 401
    return response


if __name__ == '__main__':
    app.run(debug=os.environ.get('DEBUG', False))
