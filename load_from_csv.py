from models import Player, Question, Points, Theme
from sqlalchemy import desc
import datetime
import db
import csv


class PlayerDict:
    player_order = ["Hanka","Kača","Dark","Lama","Radek","Wal","Peťa","Mates","Barča","Aleš"]
    id_dict = {}

    def __init__(self, names):
        players = Player.query.all()
        for player in players:
            self.id_dict[player.name] = player.id
        print(self.id_dict)


def process_csv(file):
    with open(file, "r", encoding="utf-8") as f:
        c = csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        line_count = 0
        for row in c:
            if line_count == 0:
                pass
            elif line_count == 1:
                PlayerDict(row[5:15])
            else:
                process_one_line(row)
            line_count += 1


def process_one_line(lst):
    theme_id = process_theme(lst[0:3])
    question_id = process_question(lst[2:5]+lst[15:16], theme_id)
    process_points(lst[5:15], question_id)


def process_theme(lst):
    if lst[0]:
        new_theme = Theme(
            name=lst[0],
            player_id=PlayerDict.id_dict[lst[1]],
            date=datetime.datetime.strptime(lst[2], "%d. %m. %Y")
        )
        db.session.add(new_theme)
        db.session.flush()
        db.session.refresh(new_theme)
    else:
        new_theme = Theme.query.order_by(desc(Theme.id)).first()
    return new_theme.id


def process_question(lst, theme_id):
    print(lst)
    new_question = Question(
            text=lst[1],
            player_id=PlayerDict.id_dict[lst[2]],
            theme_id=theme_id,
            date=datetime.datetime.strptime(lst[0], "%d. %m. %Y"),
            comments=lst[3]
    )
    db.session.add(new_question)
    db.session.flush()
    db.session.refresh(new_question)
    return new_question.id


def process_points(lst, question_id):
    all_points = []
    for i, num in enumerate(lst):
        if num:
            if float(num) != 0:
                all_points.append({"id": PlayerDict.id_dict[PlayerDict.player_order[i]],
                               "points": num})
    for p in all_points:
        new_points = Points(
            player_id=p["id"],
            question_id=question_id,
            points=p["points"],
            win=len(all_points) == 1
        )
        db.session.add(new_points)
        db.session.commit()
