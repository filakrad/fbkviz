
from flask import Flask, render_template, request
from sqlalchemy import desc
import config
import db

import question as q_module
import score
import attachment
import time_calc

from models import Player, Question, Theme

app = Flask(__name__)

app.config.from_object(config.DevelopmentConfig)
app.jinja_env.add_extension('jinja2.ext.do')


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


@app.route('/')
def index():
    try:
        q = q_module.get_random_question()
        attachment.append_attachment(q)
        print(db.engine.pool.status())
        return render_template("main_page.html", index_page=True, question=q)
    except:
        db.init_db()
        return "db initialized"


@app.route('/questions')
def show_questions():
    questions = q_module.get_all_questions()
    span_list = q_module.get_span_list(questions)
    print(span_list)
    print(db.engine.pool.status())
    return render_template("questions.html", questions_page=True,
            question=questions, span_list=span_list, prev_id=2, next_id=4)


@app.route('/scores')
def show_scores():
    scores = score.get_players_score()
    score_table = score.get_players_score_table()
    print(db.engine.pool.status())
    return render_template("players.html", score_page=True,
            score_table=score_table, simple_scores=scores)


@app.route('/insert_player',methods=['GET', 'POST'])
def insert_player():
    if request.method == 'POST':
        name = request.form.get('name')
        date_start = request.form.get('date_start')
        try:
            new_player = Player(
                name=name,
                date_start=date_start
            )
            db.session.add(new_player)
            db.session.commit()
            return "New player added. Player id={}".format(new_player.id)
        except Exception as e:
            return str(e)
    print(db.engine.pool.status())
    return render_template("insert_player.html", insert_player_page=True)


def row2dict(row, headers):
    d = {}
    for key in headers:
        d[key] = row.__dict__[key]
    return d


@app.route('/insert_theme',methods=['GET', 'POST'])
def insert_theme():
    last_theme = Theme.query.order_by(desc(Theme.date)).limit(1).all()[0]
    next_monday = time_calc.get_next_monday(last_theme.date)
    players = Player.query.all()
    head = ["id", "name"]
    players = [row2dict(p, head) for p in players]
    new_theme = None
    if request.method == 'POST':
        name = request.form.get('name')
        player_id = int(request.form.get('player'))
        print(player_id)
        date = request.form.get('date')
        try:
            new_theme = Theme(
                name=name,
                player_id=player_id,
                date=date
            )
            db.session.add(new_theme)
            db.session.commit()
        except Exception as e:
            return str(e)
    print(db.engine.pool.status())
    return render_template("insert_theme.html", insert_theme_page=True,
                           players=players, inserted=new_theme, default_date=next_monday)


@app.route('/insert_question',methods=['GET', 'POST'])
def insert_question():
    players = Player.query.all()
    themes = Theme.query.order_by(desc(Theme.date)).all()
    print(players)
    print(players[0])
    head = ["id", "name"]
    players = [row2dict(p, head) for p in players]
    themes = [row2dict(t, head) for t in themes]
    new_question = None
    if request.method == 'POST':
        new_question = q_module.insert_question(request)
        score.insert_points(request, new_question.id)
    last_question = Question.query.order_by(desc(Question.date)).limit(1).all()[0]
    next_day = time_calc.get_next_day(last_question.date)
    last_winner = score.get_winner(last_question.id)
    rearrange_players(players, last_winner)
    print(players)
    print(db.engine.pool.status())
    return render_template("insert_question.html", insert_question_page=True,
                           players=players, themes=themes, inserted=new_question,
                           default_date=next_day)


@app.route('/question/<int:id>/')
def present_question_modal(id):
    print("id {}".format(id))
    question = q_module.get_question_by_id(id)
    print(question)
    attachment.append_attachment(question)
    print(question["attachments"])
    all_points = score.get_question_score(question["id"])
    next_id = question['id'] + 1
    prev_id = question['id'] - 1
    return render_template("question_modal.html",  question=question,
                           points=all_points,
                           next_id=next_id, prev_id=prev_id)


@app.route('/minimal/')
def minimal_fct():
    return render_template("minimal.html")


@app.route('/import_csv/', methods=['GET', 'POST'])
def import_csv():
    import load_from_csv
    if request.method == 'POST':
        if 'in_csv' not in request.files:
            print(request.files)
            attach = None
        else:
            attach = attachment.save_attachments(request.files['in_csv'])
        load_from_csv.process_csv(attachment.get_path(attach))
        attachment.delete_attachment(attach)
    return render_template("import_csv.html")


@app.route('/update_question/<int:id>/', methods=['GET', 'POST'])
def update_question():
    print("id {}".format(id))
    question = q_module.get_question_by_id(id)


def rearrange_players(players, top_player_id):
    if top_player_id is None:
        return
    for i, p in enumerate(players):
        if p["id"] == top_player_id:
            break
    else:
        return
    top_player = players.pop(i)
    players.insert(0, top_player)


if __name__ == "__main__":
    app.run(debug=True, port=5957)
