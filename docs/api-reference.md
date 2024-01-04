![](./logo.png)

# Stargazer Framework API reference

All Stargazer nodes operate using the Stargazer Framework API. This document is the definite authority on the API.

All Stargazer API calls require token authentication. To known which token type is required for each call, the following variables are used:

`$TOKEN`: any token.

`$USER_TOKEN`: user tokens.

`$COMPUTE_TOKEN`: compute tokens.

`$MANAGER_TOKEN`: manager tokens.

When response data is not documented, it means the call returns either `"success"` or `"failure"` depending on what happened.

## Authentication

All Stargazer nodes require an authentication token to be passed as a HTTP header in its API calls:

`$ curl -X POST -H 'Authorization: $TOKEN'`

## Common API calls

The following API calls can be answered by all Stargazer nodes types :

**common/version**

Returns the current node version.
```
$ curl \
-H 'Authorization: $TOKEN \
-H 'Content-Type: application/json' \
$ENDPOINT/api/version
```

Response data is formated as follows:
```
{
    "version": version
}
```

**common/type**

Returns the node type.
```
$ curl \
-H 'Authorization: $TOKEN \
-H 'Content-Type: application/json' \
$ENDPOINT/api/type
```

Response data is formated as follows:
```
{
    "type": type
}
```

## Authentication gateway specific API calls

The following API calls can only be answered by Stargazer authentication gateway nodes :

**token/create**

Registers a new authentication token. Can only be used by authenticating with an admin token. Requires an expiration date to be specified, as well as a boolean specifying if the token is an admin token or not.
```
$ curl \
-H 'Authorization: $USER_TOKEN \
-H 'Content-Type: application/json' \
-d '$REQUEST' \
$ENDPOINT/api/token/create
```

The request must be formated as follows, with `type` being either `"user"`, `"manager"`, or `"compute"`, and `expiration` being a MariaDB DATETIME representing the expiration date.
```
{
    "type": type,
    "expiration_date": expiration_date
}
```

**token/revoke**

Revokes an existing authentication token. Can only be used by authenticating with an admin token. Effective immediately.
```
$ curl \
-H 'Authorization: $USER_TOKEN \
-H 'Content-Type: application/json' \
-d '{"token": "$TOKEN_TO_REVOKE"}' \
$ENDPOINT/api/token/revoke
```

**token/authenticate**

Authenticates a token against the database. Returns the roles of the token.
```
$ curl \
-H 'Authorization: $TOKEN \
-H 'Content-Type: application/json' \
-d '{"token": "$TOKEN_TO_AUTHENTICATE"}' \
$ENDPOINT/api/token/authenticate
```

The response data is formated as follows:
```
{
    "type": type,
    "valid": is_valid
}
```

## Compute node specific API calls

The following API calls can only be answered by Stargazer compute nodes :

**compute/update**

Updates the state of the universe on the compute node.
```
$ curl \
-H 'Authorization: $MANAGER_TOKEN \
-H 'Content-Type: application/json' \
-d '$STATE' \
$ENDPOINT/api/compute/update
```

`$STATE` must be formated as an array of Stargazer bodies:
```
{
    "body": [
        body0,
        ...,
        bodyn
    ]
}
```

**compute/configure**

Sets the coupling constants to be used in further computations, as well as the timestep.
```
$ curl \
-H 'Authorization: $MANAGER_TOKEN \
-H 'Content-Type: application/json' \
-d '$CONSTANTS' \
$ENDPOINT/api/compute/configure
```

`$CONSTANTS` must be formated as an array:
```
{
    "timestep": timestep,
    "gravity": gravitational_constant,
    "electrostatic": electrostatic_constant
}
```

**compute/assign**

Assigns a range of bodies to perform further computations on.
```
$ curl \
-H 'Authorization: $MANAGER_TOKEN \
-H 'Content-Type: application/json' \
-d '$BODIES' \
$ENDPOINT/api/compute/assign
```

`$BODIES` must provide the ID for the first and last bodies of the range.:
```
{
    "start": start,
    "end": end
}
```

**compute/potential/gravity**

Returns the gravitational potential energy of the bodies.
```
$ curl \
-H 'Authorization: $MANAGER_TOKEN \
-H 'Content-Type: application/json' \
$ENDPOINT/api/compute/potential/gravity
```

The results are formated as an array:
```
{
    potential: [
        p0,
        ...
        pn
    ]
}
```

**compute/potential/electrostatic**

Returns the electrostatic potential energy of the bodies.
```
$ curl \
-H 'Authorization: $MANAGER_TOKEN \
-H 'Content-Type: application/json' \
$ENDPOINT/api/compute/potential/electrostatic
```

The results are formated as an array:
```
{
    potential: [
        p0,
        ...
        pn
    ]
}
```

**compute/force/gravity**

Returns the gravitational force vector acting on the bodies.
```
$ curl \
-H 'Authorization: $MANAGER_TOKEN \
-H 'Content-Type: application/json' \
$ENDPOINT/api/compute/force/gravity
```

The vectors are formated as an array:
```
{
    force: [
        {
            "x": x,
            "y": y,
            "z": z
        },

        ...

        {
            "x": x,
            "y": y,
            "z": z
        }
    ]
}
```

**compute/force/electrostatic**

Returns the electrostatic force vector acting on the bodies.
```
$ curl \
-H 'Authorization: $MANAGER_TOKEN \
-H 'Content-Type: application/json' \
$ENDPOINT/api/compute/force/electrostatic
```

The vectors are formated as an array:
```
{
    force: [
        {
            "x": x,
            "y": y,
            "z": z
        },

        ...

        {
            "x": x,
            "y": y,
            "z": z
        }
    ]
}
```

**compute/integrate**

Performs numerical integration on the bodies, returning new positions, velocities, accelerations, and forces for the bodies.
```
$ curl \
-H 'Authorization: $MANAGER_TOKEN \
-H 'Content-Type: application/json' \
$ENDPOINT/api/compute/integrate
```

The response data is formated as an array of Stargazer bodies:

```
{
    "bodies": [
        body0,
        ...
        bodyn
    ]
}
```


## Manager node specific API calls

The following API calls can only be answered by Stargazer manager nodes :

**manager/register**

Clients sending the following request register themselves as compute nodes to the manager node.
```
$ curl \
-H 'Authorization: $COMPUTE_TOKEN \
-H 'Content-Type: application/json' \
-d '$REQUEST' \
$ENDPOINT/api/manager/register
```

`$REQUEST` must be formatted as follows, providing the URI on which the compute node is reachable:
```
{
    "compute_endpoint": uri
}
```

**manager/unregister**

Compute nodes can notify the managers that they are no longer available using this method.
```
$ curl \
-H 'Authorization: $COMPUTE_TOKEN \
-H 'Content-Type: application/json' \
$ENDPOINT/api/manager/unregister
```

**manager/configure**

Users can configure the manager nodes for further simulations.
```
$ curl \
-H 'Authorization: $USER_TOKEN \
-H 'Content-Type: application/json' \
-d '$CONFIGURATION'
$ENDPOINT/api/manager/configure
```

`$CONFIGURATION` must be formatted as such:
```
{
    "constants": {
        "timestep": timestep,
        "gravity": gravitational_constant,
        "electrostatic": electrostatic_constant
    },
    "bodies": [
        body0,
        ...
        bodyn
    ]
}
```

**manager/simulate**

Runs a simulation.
```
$ curl \
-H 'Authorization: $USER_TOKEN \
-H 'Content-Type: application/json' \
-d '$CONFIGURATION'
$ENDPOINT/api/manager/simulate
```

`$CONFIGURATION` must be formatted as such:
```
{
    "duration": duration
}
```

The response data is an XYZ file.
