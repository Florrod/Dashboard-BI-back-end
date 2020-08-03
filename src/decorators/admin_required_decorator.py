from functools import wraps
from flask_jwt_extended import get_jwt_identity
from models import Enterprise
from exceptions.not_allowed_error import NotAllowedError


def admin_required(f): #recibe una función por parametro
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity() #nos devuelve un id asociado al access token que te pasan en la cabecera
        if not current_user_id:
            raise NotAllowedError()
        current_user = Enterprise.get_some_user_id(current_user_id) #instancia de enterprise loggeada
        if not current_user or not current_user.is_admin: #clausulas de guarda
            raise NotAllowedError()
        kwargs["user"] = current_user #Al diccionario le añadimos la clave user
        return f(*args, **kwargs)
    return decorated_function