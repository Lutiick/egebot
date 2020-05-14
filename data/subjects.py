import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase

class Subjects(SqlAlchemyBase):
    __tablename__ = 'subjects'
    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    exercises_numbers = orm.relation("ExercisesNumbers", back_populates='subject')