import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship


class ExercisesNumbers(SqlAlchemyBase):
    __tablename__ = 'exercises_numbers'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    ex_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    ex_number = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    subject_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("subjects.id"))
    subject = orm.relation('Subjects')
    exercises = orm.relation('Exercises', back_populates='exercise_number')
    reference = orm.relation('References', uselist=False, back_populates='exercise_number')