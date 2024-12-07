from flask_sqlalchemy import SQLAlchemy
from app.config import environment, SCHEMA

db = SQLAlchemy()

def add_prefix_for_prod(attr):
    if environment == "production":
        return f"{SCHEMA}.{attr}"
    else:
        return attr
