import functools
from flask import request, jsonify

current_user = {"role":"guest","username":"guest"}

def auth_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization","")
        if not auth_header.startswith("Bearer"):
            return jsonify({"error":"Unauthorized"}),401
        token = auth_header.split(" ")[1]
        # interpret token
        if token == "fake-jwt-token-admin":
            global current_user
            current_user = {"role":"admin","username":"admin"}
        else:
            current_user = {"role":"guest","username":"guest"}

        return f(*args, **kwargs)
    return decorated
