from flask import Flask, request, jsonify
import requests
import hashlib
import os

# Initialize Flask
app = Flask(__name__)

# Table of registered compute nodes
# First element is the token hash
# Second element is the compute node's URI
registered = []

# Simulation settings
timestep = 1e-12
gravity = 6.67408e-11
electrostatic = 8.9875517873681764e9  # 1 / (4 * pi * epsilon_0)

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
    auth = '{}/api/token/authenticate'.format(os.environ.get('AUTH_ENDPOINT'))
    response = requests.post(auth,
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


@app.route('/api/manager/register', methods=['POST'])
def api_manager_register():
    if not authenticate(request, 'compute'):
        return jsonify({'success': False}), 401

    # Get the compute node's URI
    uri = request.json.get('compute_endpoint')

    # Check if the URI is provided and valid
    if not uri:
        return jsonify({'success': False}), 400
    if not uri.startswith('http://') and not uri.startswith('https://'):
        return jsonify({'success': False}), 400

    # Hash the token
    token = request.headers.get('Authorization')
    token = hashlib.sha256(token.split(' ')[1].encode('utf-8')).hexdigest()

    # Check if the compute node token is already registered
    for node in registered:
        if node[0] == token:
            return jsonify({'success': False}), 409

    # Check if the compute node URI is already registered
    for node in registered:
        if node[1] == uri:
            return jsonify({'success': False}), 409

    # Register the node
    registered.append([token, uri])

    return jsonify({'success': True}), 200


@app.route('/api/manager/unregister', methods=['POST'])
def api_manager_unregister():
    if not authenticate(request, 'compute'):
        return jsonify({'success': False}), 401

    # Hash the token
    token = request.headers.get('Authorization')
    token = hashlib.sha256(token.split(' ')[1].encode('utf-8')).hexdigest()

    # Check if the compute node token is registered
    for node in registered:
        if node[0] == token:
            registered.remove(node)
            return jsonify({'success': True}), 200

    return jsonify({'success': False}), 404


@app.route('/api/manager/configure', methods=['POST'])
def api_manager_configure():
    if not authenticate(request, 'user'):
        return jsonify({'success': False}), 401

    # Retrieve the variables from the request
    timestep = request.json.get('constants').get('timestep')
    gravity = request.json.get('constants').get('gravity')
    electrostatic = request.json.get('constants').get('electrostatic')
    bodies = request.json.get('bodies')

    # Check if the variables are provided
    if not timestep or not gravity or not electrostatic or not bodies:
        return jsonify({'success': False}), 400

    # Check if the variables are valid
    if not isinstance(timestep, float) or not isinstance(gravity, float) or not isinstance(electrostatic, float):
        return jsonify({'success': False}), 400

    # Check if the bodies are provided
    if not isinstance(bodies, list):
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

        # Check if the timestep is valid
        if timestep <= 0:
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


@app.route('/api/manager/simulate', methods=['POST'])
def api_manager_simulate():
    if not authenticate(request, 'user'):
        return jsonify({'success': False}), 401

    # Retrieve the duration from the request
    duration = request.json.get('duration')

    # Check if the duration is provided
    if not duration:
        return jsonify({'success': False}), 400

    # Check if the duration is valid
    if not isinstance(duration, float):
        return jsonify({'success': False}), 400
    if duration <= 0:
        return jsonify({'success': False}), 400

    # Log the number of bodies
    print('{} bodies to simulate'.format(len(bodies)))

    # Simulate the universe
    for i in range(int(duration / timestep)):
        # Log the current iteration
        print('Iteration {}/{}'.format(i, int(duration / timestep)))

        # Log the number of compute nodes
        print('{} compute nodes available'.format(len(registered)))

        # Configure the compute nodes
        for node in registered:
            requests.post('{}/api/compute/configure'.format(node[1]),
                          json={'constants': {'timestep': timestep,
                                              'gravity': gravity,
                                              'electrostatic': electrostatic},
                                'bodies': bodies},
                          timeout=5)
            print('Configured compute node {}'.format(node[1]))

        # Send the updated bodies to the compute nodes
        for node in registered:
            requests.post('{}/api/compute/bodies'.format(node[1]),
                          json={'body': bodies},
                          timeout=5)
            print('Refreshed bodies on compute node {}'.format(node[1]))

        # Assign a range of bodies to each registered compute node
        for node in registered:
            start = int(len(bodies) / len(registered) * registered.index(node))
            end = int(len(bodies) / len(registered) * (registered.index(node) + 1))
            requests.post('{}/api/compute/assign'.format(node[1]),
                          json={'start': start,
                                'end': end},
                          timeout=5)
            print('Assigned bodies {}-{} to compute node {}'.format(start, end, node[1]))

    return jsonify({'success': True}), 200


if __name__ == '__main__':
    app.run(debug=os.environ.get('DEBUG', False))
