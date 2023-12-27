![](./logo.png)

# Stargazer Framework API reference

All Stargazer nodes operate using the Stargazer Framework API. This document is the definite authority on the API.

## Authentication

All Stargazer nodes require an authentication token to be passed as a HTTP header in its API calls:

`$ curl -X POST -H 'Authorization: $TOKEN'`

## Common API calls

The following API calls can be answered by all Stargazer nodes types :

**version**

Returns the current node version.
```
$ curl \
-H 'Authorization: $TOKEN \
-H 'Content-Type: application/json' \
$ENDPOINT/api/version
```

**type**

Returns the node type.
```
$ curl \
-H 'Authorization: $TOKEN \
-H 'Content-Type: application/json' \
$ENDPOINT/api/type
```

## Authentication gateway specific API calls

The following API calls can only be answered by Stargazer authentication gateway nodes :

**token/create**

Registers a new authentication token. Can only be used by authenticating with an admin token. Requires an expiration date to be specified, as well as a boolean specifying if the token is an admin token or not.
```
$ curl \
-H 'Authorization: $TOKEN \
-H 'Content-Type: application/json' \
-d {"admin": "true", "expiration": "90d"}
$ENDPOINT/api/token/create
```

**token/revoke**

Revokes an existing authentication token. Can only be used by authenticating with an admin token. Effective immediately.
```
$ curl \
-H 'Authorization: $TOKEN \
-H 'Content-Type: application/json' \
-d {"token": "$TOKEN_TO_REVOKE"}
$ENDPOINT/api/token/revoke
```

**token/authenticate**

Authenticates a token against the database.
```
$ curl \
-H 'Authorization: $TOKEN \
-H 'Content-Type: application/json' \
-d {"token": "$TOKEN_TO_REVOKE"}
$ENDPOINT/api/token/authenticate
```

## Compute node specific API calls

The following API calls can only be answered by Stargazer compute nodes :

**aaaa**

Returns aaaaaaa.
```
$ curl \
-H 'Authorization: $TOKEN \
-H 'Content-Type: application/json' \
$ENDPOINT/api/aaaaa
```

## Manager node specific API calls

The following API calls can only be answered by Stargazer manager nodes :