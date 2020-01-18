from models import Player
from models import Theme
from models import Question
from models import Points
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased
import db
import attachment


def row2dict(row, headers):
    return {i: row[i] if row[i] is not None else '' for i in headers}


def get_all_questions():
    '''
    Gets all data expected in /question web page
    :return: list of dictionaries
    '''
    pt_alias = aliased(Player)  # join Player and Theme
    pa_alias = aliased(Player)  # join Player and Answer
    questions_query = db.session.query(
        Question.id.label('id'),
        Question.date.label('date'),
        Question.text.label('text'),
        Question.comments.label('comments'),
        Player.name.label('by'),
        Theme.name.label('theme_name'),
        pt_alias.name.label('theme_by'),
        Points.id.label('answer_id'),
        pa_alias.name.label('won')
    ).join(Player, Question.player_id == Player.id).join(
        Theme, Question.theme_id == Theme.id).join(
        pt_alias, Theme.player_id == pt_alias.id).join(
        Points, and_(Question.id == Points.question_id, Points.win == True), isouter=True).join(
        pa_alias, Points.player_id == pa_alias.id, isouter=True).order_by(Question.date)
    questions = db.session.execute(questions_query)
    head = questions.keys()
    questions_list = [row2dict(s, head) for s in questions]
    return questions_list


def get_span_list(questions_list):
    '''
    The table in /questions web page has some row spans, because questions are grouped by theme.
    This function finds how large should span be.
    :param questions_list: list of all questions
    :return: list of rowspan lengths
    '''
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
    return span_list


def get_question_by_id(qid):
    '''
    Search database for questions with id qid
    :param qid: id of desired question
    :returns: question transformed to dictionary
    '''
    question = Question.query.filter(Question.id == qid).all()
    return question_to_dict(question)


def get_random_question():
    '''
    Search database for questions and returns random one
    :returns: question transformed to dictionary
    '''
    question = Question.query.order_by(func.random()).limit(1)
    return question_to_dict(question)


def question_to_dict(question):
    '''
    Translates Question from DB to dictionary
    :param question: as returned by db
    :return: question as dict
    '''
    head = question[0].__table__.columns.keys()
    question_dict = {key: question[0].__dict__[key] for key in head}
    correct_answer_check(question_dict)
    try:
        return question_dict
    except NameError:
        '''dict wasn't generated for some reason'''
        return {}


def correct_answer_check(q_dict):
    '''
    Check if there is correct_answer value in a dict. If not, it is supplemented with some error text.
    If this key is missing, it is added.
    :param q_dict: dictionary containing correct_answer key
    '''
    missing_text = "Nenašel jsem správnou odpověď"
    key = "correct_answer"
    try:
        if q_dict[key] is None or q_dict[key] == "":
            q_dict[key] = missing_text
    except KeyError:
        q_dict[key] = missing_text


def insert_question(request):
    text = request.form.get('text')
    player_id = int(request.form.get('player_question'))
    theme_id = int(request.form.get('theme'))
    date = request.form.get('date')
    comments = request.form.get('comments')
    print(request.form)
    if 'attachments' not in request.files:
        print(request.files)
        attach = None
    else:
        attach = attachment.save_attachments(request.files['attachments'])
    correct_answer = request.form.get('correct_answer')
    try:
        new_question = Question(
            text=text,
            player_id=player_id,
            theme_id=theme_id,
            date=date,
            comments=comments,
            attachments=attach,
            correct_answer=correct_answer
        )
        db.session.add(new_question)
        db.session.flush()
        db.session.refresh(new_question)
    except Exception as e:
        return str(e)
    print("new question", new_question)
    return new_question
