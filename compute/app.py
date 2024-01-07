from flask import Flask, request, jsonify
import requests
import os

# Initialize Flask
app = Flask(__name__)

# Simulation settings
timestep = 1e-12
gravity = 6.67408e-11
electrostatic = 8.9875517873681764e9  # 1 / (4 * pi * epsilon_0)

# Range of bodies to perform computations on
range_start = 0
range_end = 0

# List of bodies in the simulation
bodies = []


# Object describing a Stargazer body
class Body:
    def __init__(self, position, velocity, acceleration, force, mass, electrostatic_charge):
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.force = force
        self.mass = mass
        self.electrostatic_charge = electrostatic_charge


# Register to the manager node
manager = os.environ.get('MANAGER_ENDPOINT')
print('Attempting registration with manager node at {}...'.format(manager))
response = requests.post('{}/api/manager/register'.format(manager),
                         headers={'Authorization': os.environ.get('TOKEN')},
                         json={'compute_endpoint': os.environ.get('ENDPOINT')},
                         timeout=5)
if not response.json().get('success'):
    print('FATAL: Failed to register with the manager node.')
    exit(1)
else:
    print('Registered.')


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
            return jsonify({'success': False}), 401
    return jsonify({'version': os.environ.get('STARGAZER_VERSION')}), 200


@app.route('/api/common/type', methods=['POST'])
def api_common_type():
    with app.app_context():
        if not authenticate(request):
            return jsonify({'success': False}), 401
    return jsonify({'version': os.environ.get('STARGAZER_TYPE')}), 200


@app.route('/api/compute/update', methods=['POST'])
def api_compute_update():
    if not authenticate(request, 'manager'):
        return jsonify({'success': False}), 401

    # Check if the bodies are provided
    if not isinstance(request.json.get('bodies'), list):
        return jsonify({'success': False}), 400

    # Retrieve all bodies from the request
    bodies = []
    for body in request.json.get('bodies'):
        position = body.get('position')
        velocity = body.get('velocity')
        acceleration = body.get('acceleration')
        force = body.get('force')
        mass = body.get('value').get('mass')
        electrostatic_charge = body.get('value').get('electrostatic_charge')

        # Check if the required data is provided
        if not position or not velocity or not acceleration or not force or not mass or not electrostatic_charge:
            return jsonify({'success': False}), 400

        # Check if the data types are valid
        if not isinstance(position, dict) or not isinstance(velocity, dict) or not isinstance(acceleration, dict) or not isinstance(force, dict) or not isinstance(mass, float) or not isinstance(electrostatic_charge, float):
            return jsonify({'success': False}), 400

        # Check if the vectors valid
        if not isinstance(position.get('x'), float) or not isinstance(position.get('y'), float) or not isinstance(position.get('z'), float):
            return jsonify({'success': False}), 400
        if not isinstance(velocity.get('x'), float) or not isinstance(velocity.get('y'), float) or not isinstance(velocity.get('z'), float):
            return jsonify({'success': False}), 400
        if not isinstance(acceleration.get('x'), float) or not isinstance(acceleration.get('y'), float) or not isinstance(acceleration.get('z'), float):
            return jsonify({'success': False}), 400
        if not isinstance(force.get('x'), float) or not isinstance(force.get('y'), float) or not isinstance(force.get('z'), float):
            return jsonify({'success': False}), 400

        # Create vectors from the retrieved variables
        position = [position.get('x'), position.get('y'), position.get('z')]
        velocity = [velocity.get('x'), velocity.get('y'), velocity.get('z')]
        acceleration = [acceleration.get('x'), acceleration.get('y'), acceleration.get('z')]
        force = [force.get('x'), force.get('y'), force.get('z')]

        # Create the body
        bodies.append(Body(position, velocity, acceleration, force, mass, electrostatic_charge))

    return jsonify({'success': True}), 200


@app.route('/api/compute/configure', methods=['POST'])
def api_compute_configure():
    if not authenticate(request, 'manager'):
        return jsonify({'success': False}), 401

    # Retrieve the variables from the request
    timestep = request.json.get('constants').get('timestep')
    gravity = request.json.get('constants').get('gravity')
    electrostatic = request.json.get('constants').get('electrostatic')

    # Check if the variables are provided
    if not timestep or not gravity or not electrostatic:
        return jsonify({'success': False}), 400

    # Check if the variables are valid
    if not isinstance(timestep, float) or not isinstance(gravity, float) or not isinstance(electrostatic, float):
        return jsonify({'success': False}), 400
    if timestep <= 0:
        return jsonify({'success': False}), 400

    return jsonify({'success': True}), 200


@app.route('/api/compute/assign', methods=['POST'])
def api_compute_assign():
    if not authenticate(request, 'manager'):
        return jsonify({'success': False}), 401

    # Retrieve the range from the request
    range_start = request.json.get('range').get('start')
    range_end = request.json.get('range').get('end')

    # Check if the range is provided
    if not range_start or not range_end:
        return jsonify({'success': False}), 400

    # Check if the range is valid
    if not isinstance(range_start, int) or not isinstance(range_end, int):
        return jsonify({'success': False}), 400
    if range_start < 0 or range_end < 0:
        return jsonify({'success': False}), 400
    if range_start > range_end:
        return jsonify({'success': False}), 400

    return jsonify({'success': True}), 200


@app.route('/api/compute/potential/gravity', methods=['POST'])
def api_compute_potential_gravity():
    if not authenticate(request, 'manager'):
        return jsonify({'success': False}), 401
    return jsonify({'success': True}), 200


@app.route('/api/compute/potential/electrostatic', methods=['POST'])
def api_compute_potential_electrostatic():
    if not authenticate(request, 'manager'):
        return jsonify({'success': False}), 401
    return jsonify({'success': True}), 200


@app.route('/api/compute/force/gravity', methods=['POST'])
def api_compute_force_gravity():
    if not authenticate(request, 'manager'):
        return jsonify({'success': False}), 401
    return jsonify({'success': True}), 200


@app.route('/api/compute/force/electrostatic', methods=['POST'])
def api_compute_force_electrostatic():
    if not authenticate(request, 'manager'):
        return jsonify({'success': False}), 401
    return jsonify({'success': True}), 200


@app.route('/api/compute/integrate', methods=['POST'])
def api_compute_integrate():
    if not authenticate(request, 'manager'):
        return jsonify({'success': False}), 401
    return jsonify({'success': True}), 200


if __name__ == '__main__':
    app.run(debug=os.environ.get('DEBUG', False))
