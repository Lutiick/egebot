import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship


class References(SqlAlchemyBase):
    __tablename__ = 'references'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    # images urls list, splited by comma
    images = sqlalchemy.Column(sqlalchemy.String)
    exercise_number_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("exercises_numbers.id"))
    exercise_number = orm.relation('ExercisesNumbers')