from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from random import randrange, choice
from test import *
import sqlalchemy
from data import db_session
from data.exercises import Exercises
from data.exercises_numbers import ExercisesNumbers
from data.subjects import Subjects
from data.references import References
import logging
import os
 
TOKEN = open('token.txt', 'r').read()

SUBJ_CHOOSE = 1
VARIANT_CHOOSE = 2
TEST = 3
MOVETO = 4
REF = 5
TEST_ONE_CHOOSE = 6

subject_choose_keyboard = ReplyKeyboardMarkup([['Математика', 'Русский'], ['Физика', 'Информатика']], one_time_keyboard=True)
variant_choose_keyboard = ReplyKeyboardMarkup([['Вернуться', 'Сгенерировать вариант'], ['Решать задачи под номером X', 'Получить справку по номеру X']], one_time_keyboard=True)


def get_reference(subject, number):
    session = db_session.create_session()
    q = session.query(ExercisesNumbers).filter(
        ExercisesNumbers.ex_number == number,
        ExercisesNumbers.subject.has(name=subject)
    ).one()
    
    img_path = os.path.abspath(f'static/img/{q.reference.images}')
    result = {
        'photo': open(img_path, 'rb'),
        'caption': f'Справка по заданию {number}',
    }

    return result


def start(update, context):
    update.message.reply_text("Приветсвую\n"
                              "Этот бот поможет при подготовки к ЕГЭ")
    update.message.reply_text('Выберете предмет',
                              reply_markup=subject_choose_keyboard)
    return SUBJ_CHOOSE


def subject_choose(update, context):
    if update.message.text.strip() not in ['Математика', 'Физика', 'Информатика', 'Русский']:
        update.message.reply_text('Неккоретный запрос\nПопробуйте еще', reply_markup=subject_choose_keyboard)
        return SUBJ_CHOOSE
    context.user_data['subject'] = update.message.text
    update.message.reply_text('Что вы хотите сделать?',
                              reply_markup=variant_choose_keyboard)
    return VARIANT_CHOOSE


def variant_choose(update, context):
    if update.message.text == 'Вернуться':
        update.message.reply_text('Выберете предмет',
                                  reply_markup=subject_choose_keyboard)
        return SUBJ_CHOOSE
    elif update.message.text == 'Сгенерировать вариант':
        context.user_data['test'] = Test(context.user_data['subject'])
        update.message.reply_photo(**context.user_data['test'].question())
        return TEST
    elif update.message.text == 'Решать задачи под номером X':
        update.message.reply_text('Ввердите номер задания')
        return TEST_ONE_CHOOSE
    elif update.message.text == 'Получить справку по номеру X':
        update.message.reply_text('Ввердите номер задания')
        return REF
    else:
        update.message.reply_text('Неккоретный запрос\nПопробуйте еще', reply_markup=variant_choose_keyboard)
        return VARIANT_CHOOSE


def test_answer(update, context):
    answer = None
    test = context.user_data['test']
    if update.message.text == 'Назад':
        try:
            test.back()
        except StopIteration:
            update.message.reply_text('Это первое задание', reply_markup=test.keyboard)
            return TEST
    elif update.message.text == 'Далее':
        try:
            test.next()
        except StopIteration:
            update.message.reply_text('Это последнее задание', reply_markup=test.keyboard)
            return TEST
    elif update.message.text == 'Перейти к номеру...' or update.message.text == 'Перейти к заданию...':
            update.message.reply_text('К какому номеру вы хотите перейти?')
            return MOVETO
    elif update.message.text == 'Решение':
        update.message.reply_photo(**test.solution())
    elif update.message.text == 'Закончить':
        res = test.test_results()
        update.message.reply_text(res)
        del context.user_data['test']
        del context.user_data['subject']
        update.message.reply_text('Выберете предмет', reply_markup=subject_choose_keyboard)
        return SUBJ_CHOOSE
    elif update.message.text == 'Справка':
        update.message.reply_photo(**get_reference(context.user_data['subject'], test.current_number))
    else:
        answer = update.message.text
        test.set_answer(answer)
        update.message.reply_text(f'Ответ {answer} сохранен')

    update.message.reply_photo(**test.question()) 


def move_to(update, context):
    try:
        n = int(update.message.text.strip())
        context.user_data['test'].move_to(n)

        update.message.reply_photo(**context.user_data['test'].question())
        return TEST
    except ValueError:
        update.message.reply_text('Неправильный формат\nПопробуйте ещё')
        return MOVETO
    except StopIteration:
        update.message.reply_text('Такого номера не существует\nПопробуйте ещё')
        return MOVETO


def get_ref_of(update, context):
    subject = context.user_data['subject']
    try:
        number = int(update.message.text.strip())
        update.message.reply_photo(**get_reference(subject, number), reply_markup=variant_choose_keyboard)
    except:
        update.message.reply_text('Неккоректный запрос', reply_markup=variant_choose_keyboard)
    return VARIANT_CHOOSE


def test_one_choose(update, context):
    try:
        number = int(update.message.text.strip())
        subject = context.user_data['subject']
        context.user_data['test'] = TestOne(subject, number)
        update.message.reply_photo(**context.user_data['test'].question())
        return TEST
    except:
        update.message.reply_text('Неккоректный запрос', reply_markup=variant_choose_keyboard)
    return VARIANT_CHOOSE


def stop(update, context):
    update.message.reply_text("Пока-пока")
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    db_session.global_init('db/db.sqlite')

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SUBJ_CHOOSE: [MessageHandler(Filters.text, subject_choose)],
            VARIANT_CHOOSE: [MessageHandler(Filters.text, variant_choose)],
            TEST: [MessageHandler(Filters.text, test_answer)],
            MOVETO: [MessageHandler(Filters.text, move_to)],
            REF: [MessageHandler(Filters.text, get_ref_of)],
            TEST_ONE_CHOOSE: [MessageHandler(Filters.text, test_one_choose)]
        },
        fallbacks=[CommandHandler('quit', stop)]
    )
    dp.add_handler(conv_handler)

    dp = updater.dispatcher
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()