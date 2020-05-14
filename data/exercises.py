import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship


class Exercises(SqlAlchemyBase):
    __tablename__ = 'exercises'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    ex_solution = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    ex_answer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    ex_image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    exercise_number_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("exercises_numbers.id"))
    exercise_number = orm.relation('ExercisesNumbers')