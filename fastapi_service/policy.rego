package authz

# Default to denying access
default allow = false

# Example user and role data
users = {
    "climacs@gmail.com": "admin",
    "climacs@climacs.net": "user",
    "miguelnero.climacosa@gmail.com": "user"
}

# Allow users with "admin" role to perform POST requests
allow {
    input.method == "POST"
    users[input.token] == "admin"
}

# Allow users with "user" role to perform GET requests
allow {
    input.method == "GET"
    users[input.token] == "user"
}
