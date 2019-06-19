from sqlalchemy import Integer, String, Column
from sqlalchemy import create_engine
from sqlalchemy.ext import declarative
from passlib.apps import custom_app_context as pwd_context

Base = declarative.declarative_base()
engine = create_engine('sqlite:///my-db.db')
Base.metadata.bind = engine

class Elect(Base):
    __tablename__ = 'elect'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    description = Column(String(64))
    image = Column(String(20))
    @property
    def serialize(self):
        return {
            'ID': self.id,
            'Name': self.name,
            'Description': self.description,
            'Image': self.image
        }

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32))
    password = Column(String(64))

    def hash_password(self, password_to_be_hashed):
        self.password = pwd_context.encrypt(password_to_be_hashed)

    def verify_password(self, password_to_be_verified):
        return pwd_context.verify(password_to_be_verified, self.password)

Base.metadata.create_all(engine)