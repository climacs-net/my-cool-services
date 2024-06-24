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
    token = input.token
}

valid_admin {
    token = input.token
    role = "admin"
}
