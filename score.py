from models import Player
from models import Answer
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
        func.sum(Answer.points).label('score')
    ).join(Answer, isouter=True).group_by(Player.id).order_by(Player.id)
    scores = db.session.execute(scores_query)
    head = scores.keys()
    score_list = [row2dict(s, head) for s in scores]
    return score_list


def get_players_score_table():
    scores_query = db.session.query(
        Answer.player_id.label('player_answered'),
        Player.id.label('player_asked'),
        func.sum(Answer.points).label('score')
    ).join(Question, Answer.question_id == Question.id).join(
        Player, Question.player_id == Player.id).group_by(Player.id, Answer.player_id)

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
