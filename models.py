from database.db import db

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

class MCQHistory(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    topic = db.Column(
        db.String(100),
        nullable=False
    )

    questions = db.Column(
        db.Text,
        nullable=False
    )

class QuizScore(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    topic = db.Column(
        db.String(100),
        nullable=False
    )

    score = db.Column(
        db.Integer,
        nullable=False
    )