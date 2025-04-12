import functools
from flask import request, jsonify
import logging # Use logging

logger = logging.getLogger(__name__)

# --- Placeholder RBAC - Needs complete replacement for production ---
# This uses a hardcoded token and global state, which is insecure and not scalable.
# Replace with a proper authentication/authorization library like:
# - Flask-Login + Flask-Principal
# - Flask-Security-Too
# - Flask-JWT-Extended (for token-based auth)
# - OAuthLib/Authlib for OAuth/OIDC

current_user = {"role": "guest", "username": "guest"} # Global state - problematic

def auth_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        global current_user # Modifying global state is bad practice in web apps
        auth_header = request.headers.get("Authorization", "")
        token = None

        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        # --- Replace this fake token check ---
        if token == "fake-jwt-token-admin":
            # In a real app, you would validate the token (e.g., JWT signature/expiry)
            # and fetch user details/roles from the token payload or a database.
            current_user = {"role": "admin", "username": "admin"}
            logger.debug(f"Auth successful for admin user via fake token")
            return f(*args, **kwargs)
        else:
            # Reset to guest if token is missing or invalid (for this placeholder)
            current_user = {"role": "guest", "username": "guest"}
            logger.warning(f"Auth failed: Invalid or missing token. Header: '{auth_header[:30]}...'")
            return jsonify({"error": "Unauthorized", "message": "Valid Bearer token required"}), 401
        # --- End of fake token check ---

    return decorated

# Add role-based checks if needed, e.g.:
# def admin_required(f):
#     @auth_required
#     @functools.wraps(f)
#     def decorated(*args, **kwargs):
#         if current_user.get("role") != "admin":
#             return jsonify({"error": "Forbidden", "message": "Admin privileges required"}), 403
#         return f(*args, **kwargs)
#     return decorated
