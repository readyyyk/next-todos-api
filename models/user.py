import urllib.parse
from sqlalchemy import Column, Integer, String, Date, func

from models.crud import CRUD


def default_image(context):
    return "https://api.dicebear.com/7.x/identicon/svg?seed="+urllib.parse.quote_plus(context.get_current_parameters()["username"])


class User(CRUD):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    registered = Column(Date, nullable=False, server_default=func.now())
    image = Column(String, nullable=False, default=default_image)
