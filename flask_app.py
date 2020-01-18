
from flask import Flask, render_template, request
from sqlalchemy import desc
import config
import db

app = Flask(__name__)

app.config.from_object(config.DevelopmentConfig)
app.jinja_env.add_extension('jinja2.ext.do')


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


@app.route('/')
def index():
    # try:
        import question
        import attachment
        q = question.get_random_question()
        attachment.append_attachment(q)
        if not q["correct_answer"]:
            q["correct_answer"] = "Nenašel jsem správnou odpověď"
        print(db.engine.pool.status())
        return render_template("main_page.html", index_page=True, question=q)
    # except:
    #     db.init_db()
    #     return "db initialized"


@app.route('/questions')
def show_questions():
    import question
    questions = question.get_all_questions()
    span_list = question.get_span_list(questions)
    print(span_list)
    print(db.engine.pool.status())
    return render_template("questions.html", questions_page=True,
            question=questions, span_list=span_list, prev_id=2, next_id=4)


@app.route('/scores')
def show_scores():
    import score
    scores = score.get_players_score()
    score_table = score.get_players_score_table()
    print(db.engine.pool.status())
    return render_template("players.html", score_page=True,
            score_table=score_table, simple_scores=scores)


@app.route('/insert_player',methods=['GET', 'POST'])
def insert_player():
    if request.method == 'POST':
        from models import Player
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
    from models import Player
    players = Player.query.all()
    print(players)
    print(players[0])
    head = ["id", "name"]
    players = [row2dict(p, head) for p in players]
    new_theme = None
    if request.method == 'POST':
        from models import Theme
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
                           players=players, inserted=new_theme)


@app.route('/insert_question',methods=['GET', 'POST'])
def insert_question():
    from models import Player
    from models import Theme
    players = Player.query.all()
    themes = Theme.query.order_by(desc(Theme.date)).all()
    print(players)
    print(players[0])
    head = ["id", "name"]
    players = [row2dict(p, head) for p in players]
    themes = [row2dict(t, head) for t in themes]
    new_question = None
    if request.method == 'POST':
        import question
        import score
        new_question = question.insert_question(request)
        new_score = score.insert_points(request, new_question.id)
    print(db.engine.pool.status())
    return render_template("insert_question.html", insert_question_page=True,
                           players=players, themes=themes, inserted=new_question)


@app.route('/insert_answer',methods=['GET', 'POST'])
def insert_answer():
    from models import Player
    from models import Question
    players = Player.query.all()
    questions = Question.query.order_by(desc(Question.date)).all()
    print(questions)
    head = ["id", "name"]
    players = [row2dict(p, head) for p in players]
    head = ["id", "text"]
    questions = [row2dict(t, head) for t in questions]
    new_answer = None
    if request.method == 'POST':
        from models import Answer
        text = request.form.get('text')
        player_id = int(request.form.get('player'))
        question_id = int(request.form.get('question'))
        points = request.form.get('points')
        win = request.form.get('win') is not None
        print("\n\n{}\n\n".format(win))
        try:
            new_answer = Answer(
                text=text,
                player_id=player_id,
                question_id=question_id,
                points=points,
                win=win
            )
            db.session.add(new_answer)
            db.session.commit()
        except Exception as e:
            return str(e)
    print(db.engine.pool.status())
    return render_template("insert_answer.html", insert_answer_page=True,
                           players=players, questions=questions, inserted=new_answer)


@app.route('/question/<int:id>/')
def present_question_modal(id):
    print("id {}".format(id))
    import question as q_module
    import attachment
    import score
    question = q_module.get_question_by_id(id)
    print(question)
    attachment.append_attachment(question)
    if not question["correct_answer"]:
        question["correct_answer"] = "Nenašel jsem správnou odpověď"
    all_points = score.get_question_score(question["id"])
    next_id = question['id'] + 1
    prev_id = question['id'] - 1
    return render_template("question_modal.html",  question=question,
                           points=all_points,
                           next_id=next_id, prev_id=prev_id)


@app.route('/minimal/')
def minimal_fct():
    return render_template("minimal.html")

if __name__ == "__main__":
    app.run(debug=True, port=5957)