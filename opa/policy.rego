package authz

default allow = false

allow {
    input.method == "GET"
    valid_user
}

allow {
    input.method == "POST"
    valid_admin
}

valid_user {
    # Example: check for a valid token (this would need to be customized)
    token = input.token
    # Validate token and user (this is a placeholder for actual validation logic)
}

valid_admin {
    # Example: check for admin role (this would need to be customized)
    token = input.token
    role = "admin"
    # Validate token and role (this is a placeholder for actual validation logic)
}
