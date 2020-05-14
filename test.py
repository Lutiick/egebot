from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from random import randrange, choice, shuffle
import sqlalchemy
from data import db_session
from data.exercises import Exercises
from data.exercises_numbers import ExercisesNumbers
from data.subjects import Subjects
from data.references import References
import os


class TestExercise():
    def __init__(self, ex_number=None, ex_solution=None, ex_answer=None, ex_image=None):
        self.ex_solution = ex_solution
        self.ex_answer = ex_answer
        self.ex_image = ex_image
        self.ex_number = ex_number
    
    def check_answer(self, answer):
        if not answer:
            return False
        if self.ex_answer == answer:
            return True
        return False

class Test:
    def __init__(self, subject):
        self.subject = subject
        self.ex_list = []
        session = db_session.create_session()
        subject = session.query(Subjects).filter(Subjects.name == subject).one()
        ex_nums = subject.exercises_numbers
        for ex_num in ex_nums:
            ex = choice(ex_num.exercises)
            ex = TestExercise(
                ex_solution = ex.ex_solution,
                ex_answer = ex.ex_answer,
                ex_image = ex.ex_image,
                ex_number = ex.exercise_number.ex_number
            )
            self.ex_list.append(ex)
        self.answers = [None] * self.length
        self.n = 0

    @property
    def length(self):
        return len(self.ex_list)

    @property
    def keyboard(self):
        keyboard = []
        if self.n != 0:
            keyboard.append('Назад')
        if self.length - 1 != self.n:
            keyboard.append('Далее')
        keyboard.append('Перейти к номеру...')
        keyboard.append('Закончить')
        keyboard.append('Справка')
        if self.current.ex_solution:
            keyboard.append('Решение')
        result = []
        for i in range(len(keyboard)):
            if i % 2 == 0:
                result.append([])
            result[-1].append(keyboard[i])
        
        return ReplyKeyboardMarkup(result, one_time_keyboard=True)


    def question(self):
        caption = f"Номер {self.current_number}"
        if self.current_answer:
            caption += f'\nВаш ответ: {self.current_answer}'
        img_path = os.path.abspath(f'static/img/{self.current.ex_image}')
        
        result = {
            'photo': open(img_path, 'rb'),
            'caption': caption,
            'reply_markup': self.keyboard
        }
        return result
    
    def solution(self):
        caption = f"Решение номера {self.current_number}"
        if self.current_answer:
            caption += f'\nВаш ответ {self.current_answer}'
        img_path = os.path.abspath(f'static/img/{self.current.ex_solution}')
        
        result = {
            'photo': open(img_path, 'rb'),
            'caption': caption,
            'reply_markup': self.keyboard
        }
        return result

    def next(self):
        if self.n + 1 > self.length:
            raise StopIteration()
        self.n += 1
    
    def back(self):
        if self.n - 1 < 0:
            raise StopIteration()
        self.n -= 1
    
    def set_answer(self, n):
        self.answers[self.n] = n

    def count_answers(self):
        count = 0
        for i, ex in enumerate(self.ex_list):
            count += 1 if ex.check_answer(self.answers[i]) else 0
        return count
    
    def test_results(self):
        lst = [1 for ex in self.ex_list if ex.ex_answer is not None] # Только задания у которых есть ответы
        result = ['Результаты тестовой части']
        for i in range(len(lst)):
            ans = self.answers[i]
            if ans is None:
                cor = ''
                ans = '--'
            elif self.ex_list[i].check_answer(ans):
                cor = '+'
            else:
                cor = '-'
            res = f'{i + 1}. {ans} {cor}'
            ans = f'    ({self.ex_list[i].ex_answer})'
            result.append(res + ans)
        result.append(f'{self.count_answers()} / {len(lst)}')
        return '\n'.join(result)
    
    @property
    def current(self):
        return self.ex_list[self.n]
    
    @property
    def current_number(self):
        return self.n + 1
    
    @property
    def current_answer(self):
        return self.answers[self.n]
    
    def move_to(self, n):
        if 0 < n <= len(self.ex_list):
            self.n = n - 1
        else:
            raise StopIteration()


class TestOne(Test):
    def __init__(self, subject, number):
        self.subject = subject
        self.number = number
        self.n = 0

        self.ex_list = []
        session = db_session.create_session()
        ex_nums = session.query(ExercisesNumbers).filter(
            ExercisesNumbers.ex_number == self.number,
            ExercisesNumbers.subject.has(name=self.subject)
        ).one()
        exs = ex_nums.exercises
        shuffle(exs)

        self.ex_list = []
        for ex in exs:
            ex = TestExercise(
                ex_solution = ex.ex_solution,
                ex_answer = ex.ex_answer,
                ex_image = ex.ex_image,
                ex_number = ex.exercise_number.ex_number
            )
            self.ex_list.append(ex)
        
        self.answers = [None] * self.length

    @property
    def keyboard(self):
        keyboard = []
        if self.n != 0:
            keyboard.append('Назад')
        if self.length - 1 != self.n:
            keyboard.append('Далее')
        keyboard.append('Перейти к заданию...')
        keyboard.append('Закончить')
        keyboard.append('Справка')
        if self.current.ex_solution:
            keyboard.append('Решение')
        result = []
        for i in range(len(keyboard)):
            if i % 2 == 0:
                result.append([])
            result[-1].append(keyboard[i])
        
        return ReplyKeyboardMarkup(result, one_time_keyboard=True)
    
    @property
    def current_number(self):
        return self.number
    
    def question(self):
        caption = f"Номер {self.current_number}"
        if self.current_answer:
            caption += f'\nВаш ответ: {self.current_answer}'
            if self.current_answer:
                caption += ' +' if self.current_answer == self.current.ex_answer else ' -'

        img_path = os.path.abspath(f'static/img/{self.current.ex_image}')
        
        result = {
            'photo': open(img_path, 'rb'),
            'caption': caption,
            'reply_markup': self.keyboard
        }
        return result
