from db import Base
from sqlalchemy import Column, Integer, Date, Unicode, ForeignKey, Numeric, Boolean
from datetime import datetime


class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50))
    date_start = Column(Date, nullable=False, default=datetime.now())
    date_end = Column(Date)
    score = 0

    def __init__(self, name, date_start=datetime.now(), date_end=None):
        self.name = name
        self.date_start = date_start
        self.date_end = date_end


class Theme(Base):
    __tablename__ = 'theme'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100))
    player_id = Column(Integer, ForeignKey('player.id'))
    date = Column(Date, nullable=False, default=datetime.now())

    def __init__(self, name, player_id, date=datetime.now()):
        self.name = name
        self.player_id = player_id
        self.date = date


class Question(Base):
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    text = Column(Unicode(32768))
    player_id = Column(Integer, ForeignKey('player.id'))
    theme_id = Column(Integer, ForeignKey('theme.id'))
    date = Column(Date, nullable=False, default=datetime.now())
    comments = Column(Unicode(32768))
    attachments = Column(Unicode(128))
    correct_answer = Column(Unicode(512))

    def __init__(self, text, player_id, theme_id, date=datetime.now(), comments=None, attachments=None, correct_answer=None):
        self.text = text
        self.player_id = player_id
        self.theme_id = theme_id
        self.date = date
        self.comments = comments
        self.attachments = attachments
        self.correct_answer = correct_answer


class Points(Base):
    __tablename__ = 'points'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    question_id = Column(Integer, ForeignKey('question.id'))
    points = Column(Numeric(precision=5, scale=3))
    bonus_points = Column(Numeric(precision=5, scale=3))
    win = Column(Boolean(), nullable=False, default=False)

    def __init__(self, player_id, question_id, points=0, bonus_points=0, win=False):
        self.player_id = player_id
        self.question_id = question_id
        self.points = points
        self.bonus_points = bonus_points
        self.win = win
