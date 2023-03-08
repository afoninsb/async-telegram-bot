from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship

from settings import DB

sqlite_database = (f'postgresql://{DB["user"]}:'
                   f'{DB["password"]}@{DB["host"]}/{DB["dbname"]}')
engine = create_engine(sqlite_database)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String, unique=True)
    state = Column(String)
    voices = relationship(
        'Voice',
        back_populates='user',
        cascade="all, delete-orphan"
    )


class Voice(Base):
    __tablename__ = 'voices'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user = relationship('User', back_populates='voices')
    user_id = Column(Integer, ForeignKey('users.id'))
    file_id = Column(String, unique=True)
    file_size = Column(Integer)
    duration = Column(Integer)
    url = Column(String)


Base.metadata.create_all(bind=engine)
