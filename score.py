from models import Player
from models import Points
from models import Question
import db
from sqlalchemy import func


def row2dict(row, headers):
    d = {}
    for key in headers:
        d[key] = row[key] if row[key] is not None else 0
    return d


def get_players_score():
    scores_query = db.session.query(
        Player.id.label('id'),
        Player.name.label('name'),
        func.sum(Points.points + Points.bonus_points).label('score')
    ).join(Points, isouter=True).group_by(Player.id).order_by(Player.id)
    scores = db.session.execute(scores_query)
    head = scores.keys()
    score_list = [row2dict(s, head) for s in scores]
    return score_list


def get_players_score_table():
    scores_query = db.session.query(
        Points.player_id.label('player_answered'),
        Player.id.label('player_asked'),
        func.sum(Points.points + Points.bonus_points).label('score')
    ).join(Question, Points.question_id == Question.id).join(
        Player, Question.player_id == Player.id).group_by(Player.id, Points.player_id)

    scores = db.session.execute(scores_query)

    head = scores.keys()
    score_list = [row2dict(s, head) for s in scores]

    players = Player.query.all()
    matrix = create_score_matrix(players, score_list)
    return matrix


def create_score_matrix(players, scores):
    size = len(players) + 1
    matrix = [[0 for _ in range(size)] for _ in range(size)]
    for p in players:
        matrix[0][p.id] = p.name
        matrix[p.id][0] = p.name
    for s in scores:
        matrix[s["player_asked"]][s["player_answered"]] = s["score"]
    matrix[0][0] = ''
    return matrix


def insert_points(request, question_id):
    i = 0
    points_list = []
    while "player_points{}".format(i) in request.form:
        points_dict = {"player": int(request.form.get('player_points{}'.format(i))),
                       "points": request.form.get('points{}'.format(i)),
                       "bonus_points": request.form.get('bonus_points{}'.format(i)),
                       "win": request.form.get('win{}'.format(i))}
        if float(points_dict["points"]) + float(points_dict["bonus_points"]) > 0:
            points_list.append(points_dict)
        i += 1

    print(points_list, question_id)
    wins = 0
    for dct in points_list:
        if dct["win"]:
            wins += 1
            dct["win"] = True
        else:
            dct["win"] = False
    if wins != 1:
        print("invalid number of wins")

    for dct in points_list:
        new_points = Points(
            player_id=dct["player"],
            question_id=question_id,
            points=dct["points"],
            bonus_points=dct["bonus_points"],
            win=dct["win"]
        )
        db.session.add(new_points)
    db.session.commit()

    return 0


def get_question_score(question_id):
    query = db.session.query(
        Points.id.label('id'),
        Points.points.label('points'),
        Points.bonus_points.label('bonus_points'),
        Points.win.label('win'),
        Player.name.label('player')
    ).join(Player, Points.player_id == Player.id).filter(Points.question_id==question_id)
    points = db.session.execute(query)
    head = points.keys()
    points_list = [row2dict(s, head) for s in points]
    return points_list


