import os
dynamic_answers = []
current_topic = ""
quiz_answers = [
    "Delhi",
    "4"
]
from flask import Flask, render_template, request, session, redirect
from database.db import db
from models import User, MCQHistory, QuizScore
from services.news import get_news
from services.chatbot import ask_ai, generate_mcq, parse_mcq
import bcrypt

app = Flask(__name__)

app.secret_key = "mysecretkey"

database_url = os.getenv("DATABASE_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres123@localhost/exambot"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# Home page route
@app.route("/")
def home():
    return render_template("index.html")


# ADD STEP 4 CODE HERE ↓↓↓
@app.route("/signup", methods=["GET","POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
        ).decode("utf-8")

        new_user = User(
        name=name,
        email=email,
        password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return "User Registered Successfully"

    return render_template("signup.html")

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and bcrypt.checkpw(
            password.encode("utf-8"),
            user.password.encode("utf-8")
        ):

            session["user_email"] = email

            return redirect("/dashboard")

        else:
            return "Invalid Email or Password"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "user_email" not in session:
        return "Please Login First"

    user = User.query.filter_by(
        email=session["user_email"]
    ).first()

    total_quiz = QuizScore.query.filter_by(
        username=user.name
    ).count()

    return render_template(
        "dashboard.html",
        user=user,
        total_quiz=total_quiz
    )

@app.route("/logout")
def logout():

    session.pop("user_email", None)

    return "Logged Out Successfully"

@app.route("/news/<category>")
def news(category):

    articles = get_news(category)

    return render_template(
        "news.html",
        articles=articles
    )

@app.route("/chatbot", methods=["GET","POST"])
def chatbot():

    if request.method == "POST":

        question = request.form["question"]

        answer = ask_ai(question)

        return render_template(
            "chatbot.html",
            answer=answer
        )

    return render_template(
        "chatbot.html",
        answer=None
    )

@app.route("/mcq", methods=["GET","POST"])
def mcq():

    print("MCQ ROUTE HIT")

    if request.method == "POST":

        topic = request.form["topic"]

        print("Topic:", topic)

        questions = generate_mcq(topic)

        print("Generated successfully")

        history = MCQHistory(
            topic=topic,
            questions=questions
        )

        db.session.add(history)
        print("Added to session")

        db.session.commit()
        print("Saved to database")

        return render_template(
            "mcq.html",
            questions=questions
        )

    return render_template(
        "mcq.html",
        questions=None
    )

@app.route("/history")
def history():

    all_history = MCQHistory.query.all()

    return render_template(
        "history.html",
        history=all_history
    )

@app.route("/quiz", methods=["GET","POST"])
def quiz():

    if request.method == "POST":

        topic = request.form["topic"]

        quiz = generate_mcq(topic)

        return render_template(
            "quiz.html",
            quiz=quiz
        )

    return render_template(
        "quiz.html",
        quiz=None
    )

@app.route("/test_quiz")
def test_quiz():

    questions = [

        {
            "question":"Capital of India?",

            "options":["Mumbai","Delhi","Pune","Chennai"],

            "answer":"Delhi"
        },

        {
            "question":"2 + 2 = ?",

            "options":["2","3","4","5"],

            "answer":"4"
        }

    ]

    return render_template(
        "test_quiz.html",
        questions=questions
    )

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():

    score = 0

    answer1 = request.form["1"]
    answer2 = request.form["2"]

    if answer1 == quiz_answers[0]:
        score += 1

    if answer2 == quiz_answers[1]:
        score += 1

    return f"Your Score is {score}/2"

@app.route("/ai_quiz", methods=["GET","POST"])
def ai_quiz():

    if "user_email" not in session:
     return "Please Login First"

    global dynamic_answers, current_topic

    if request.method == "POST":

        topic = request.form["topic"]

        current_topic = topic

        raw_quiz = generate_mcq(topic)

        questions = parse_mcq(raw_quiz)

        dynamic_answers = []

        for q in questions:
            dynamic_answers.append(q["answer"])

        return render_template(
            "ai_quiz.html",
            questions=questions
        )

    return render_template(
        "quiz_start.html"
    )

@app.route("/submit_ai_quiz", methods=["POST"])
def submit_ai_quiz():

    global dynamic_answers

    score = 0

    for i in range(len(dynamic_answers)):

        user_answer = request.form.get(f"q{i+1}")

        correct_answer = dynamic_answers[i]

        print("User selected:", user_answer)
        print("Correct answer:", correct_answer)

        if user_answer == correct_answer:
            score += 1

    user = User.query.filter_by(
    email=session["user_email"]
).first()

    new_score = QuizScore(
    username=user.name,
    topic=current_topic,
    score=score
)

    db.session.add(new_score)
    db.session.commit()

    return f"Your AI Quiz Score is {score}/{len(dynamic_answers)}"

@app.route("/leaderboard")
def leaderboard():

    scores = QuizScore.query.order_by(
        QuizScore.score.desc()
    ).all()

    return render_template(
        "leaderboard.html",
        scores=scores
    )

@app.route("/admin")
def admin():

    users = User.query.all()

    return render_template(
        "admin.html",
        users=users
    )

@app.route("/delete_user/<int:id>")
def delete_user(id):

    user = User.query.get(id)

    db.session.delete(user)

    db.session.commit()

    return redirect("/admin")
# Keep this at bottom
if __name__ == "__main__":
    app.run(debug=True)