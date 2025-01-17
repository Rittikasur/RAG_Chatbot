import flask
import jwt

SECRET_KEY = "whyisitasitis"

def authenticateToken():
    auth_header = flask.request.headers.get("Authorization")
    if not auth_header:
        raise ValueError()
    
    token = auth_header.split(" ")[1]
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    return decoded_token.get("id")