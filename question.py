from models import Player
from models import Theme
from models import Question
from models import Answer
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased
import db


def row2dict(row, headers):
    d = {}
    for key in headers:
        d[key] = row[key] if row[key] is not None else ''
    return d


def get_questions():
    pt_alias = aliased(Player) # join Player and Theme
    pa_alias = aliased(Player) # join Player and Answer
    questions_query = db.session.query(
        Question.id.label('id'),
        Question.date.label('date'),
        Question.text.label('text'),
        Question.comments.label('comments'),
        Question.attachments.label('attachment_path'),
        Player.name.label('by'),
        Theme.name.label('theme_name'),
        pt_alias.name.label('theme_by'),
        Answer.id.label('answer_id'),
        pa_alias.name.label('won')
    ).join(Player, Question.player_id == Player.id).join(
        Theme, Question.theme_id == Theme.id).join(
        pt_alias, Theme.player_id == pt_alias.id).join(
        Answer, Question.id == Answer.question_id, isouter=True).join(
        pa_alias, Answer.player_id == pa_alias.id, isouter=True)
    questions = db.session.execute(questions_query)
    head = questions.keys()
    questions_list = [row2dict(s, head) for s in questions]
    span_list = []
    theme_name = questions_list[0]["theme_name"]
    idx = 0
    for q in questions_list:
        if theme_name == q["theme_name"]:
            idx += 1
        else:
            span_list.append(idx)
            theme_name = q["theme_name"]
            idx = 1
    span_list.append(idx)
    return questions_list, span_list


def get_random_question():
    '''get random question'''
    question_query = db.session.query(
        Question.id.label('id'),
        Question.text.label('text')).order_by(func.random()).limit(1)
    question = db.session.execute(question_query)
    head = question.keys()
    for q in question:
        question_out = row2dict(q, head)

    '''get corresponding answer'''
    answer_query = db.session.query(
            Answer.text.label('text')
        ).filter(and_(Answer.question_id==question_out["id"],
                         Answer.win==True))
    answer = db.session.execute(answer_query)
    head = answer.keys()
    for a in answer:
        answer_out = row2dict(a, head)
        break
    else:
        answer_out = {'text': 'Nenašel jsem správnou odpověď.'}

    return question_out, answer_out
