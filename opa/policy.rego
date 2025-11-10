package authz

# Default to denying access
default allow = false

# Example user and role data
users = {
    "climacs@gmail.com": "admin",
    "climacs@climacs.net": "user",
    "miguelnero.climacosa@gmail.com": "user"
}

# Allow users with "admin" role to perform POST requests (create users)
allow {
    input.method == "POST"
    users[input.token] == "admin"
}

# Allow authenticated users (any valid token) to perform GET requests (read users)
allow {
    input.method == "GET"
    users[input.token]
}
