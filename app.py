from werkzeug.utils import secure_filename
import os
import os
from dotenv import load_dotenv

load_dotenv()
dynamic_answers = []
current_topic = ""
quiz_answers = [
    "Delhi",
    "4"
]
from flask import Flask, render_template, request, session, redirect, flash
from database.db import db
from models import User, MCQHistory, QuizScore, ChatHistory
from services.news import get_news
from services.chatbot import ask_ai, generate_mcq, parse_mcq
import bcrypt

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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
@app.route("/signup", methods=["GET", "POST"])
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

        flash(
            "Registration Successful! Please Login.",
            "success"
        )

        return redirect("/login")

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

            flash(
                "Invalid Email or Password",
                "danger"
            )

            return redirect("/login")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "user_email" not in session:
        return redirect("/login")

    user = User.query.filter_by(
        email=session["user_email"]
    ).first()

    total_quiz = QuizScore.query.filter_by(
        username=user.name
    ).count()

    total_chat = ChatHistory.query.filter_by(
        username=user.name
    ).count()

    highest_score = db.session.query(
        db.func.max(QuizScore.score)
    ).filter(
        QuizScore.username == user.name
    ).scalar()

    if highest_score is None:
        highest_score = 0

    recent_quizzes = QuizScore.query.filter_by(
        username=user.name
    ).order_by(
        QuizScore.id.desc()
    ).limit(5).all()

    recent_chats = ChatHistory.query.filter_by(
        username=user.name
    ).order_by(
        ChatHistory.id.desc()
    ).limit(5).all()

    return render_template(
        "dashboard.html",
        user=user,
        total_quiz=total_quiz,
        total_chat=total_chat,
        highest_score=highest_score,
        recent_quizzes=recent_quizzes,
        recent_chats=recent_chats
    )
@app.route("/profile")
def profile():

    if "user_email" not in session:
        return redirect("/login")

    user = User.query.filter_by(
        email=session["user_email"]
    ).first()

    return render_template(
        "profile.html",
        user=user
    )

@app.route("/upload_profile", methods=["POST"])
def upload_profile():

    if "user_email" not in session:
        return redirect("/login")

    user = User.query.filter_by(
        email=session["user_email"]
    ).first()

    file = request.files["profile"]

    if file.filename != "":

        filename = secure_filename(file.filename)

        file.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

        user.profile_pic = filename

        db.session.commit()

    return redirect("/profile")

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    if "user_email" not in session:
        return redirect("/login")

    user = User.query.filter_by(
        email=session["user_email"]
    ).first()

    if request.method == "POST":

        user.name = request.form["name"]
        user.email = request.form["email"]

        session["user_email"] = user.email

        db.session.commit()

        flash(
            "Profile Updated Successfully",
            "success"
            )

        return redirect("/profile")
        return render_template(
        "edit_profile.html",
        user=user
    )

@app.route("/change_password", methods=["GET", "POST"])
def change_password():

    if "user_email" not in session:
        return redirect("/login")

    user = User.query.filter_by(
        email=session["user_email"]
    ).first()

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if not bcrypt.checkpw(
            current_password.encode("utf-8"),
            user.password.encode("utf-8")
        ):
            return "Current Password is Incorrect"

        if new_password != confirm_password:
            return "Passwords do not match"

        hashed_password = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        user.password = hashed_password

        db.session.commit()

        flash(
            "Password Changed Successfully",
            "success"
            )

        return redirect("/profile")

    return render_template("change_password.html")

@app.route("/logout")
def logout():

    session.pop("user_email", None)

    flash(
        "Logged Out Successfully",
        "info"
    )

    return redirect("/")
@app.route("/news/<category>")
def news(category):

    articles = get_news(category)

    return render_template(
        "news.html",
        articles=articles
    )

@app.route("/chatbot", methods=["GET","POST"])
def chatbot():

    if "user_email" not in session:
        return redirect("/login")

    if request.method == "POST":

        question = request.form["question"]

        answer = ask_ai(question)

        user = User.query.filter_by(
            email=session["user_email"]
        ).first()

        history = ChatHistory(
            username=user.name,
            question=question,
            answer=answer
        )

        db.session.add(history)
        db.session.commit()

        return render_template(
            "chatbot.html",
            answer=answer
        )

    return render_template(
        "chatbot.html",
        answer=None
    )

@app.route("/chat_history")
def chat_history():

    if "user_email" not in session:
        return redirect("/login")

    user = User.query.filter_by(
        email=session["user_email"]
    ).first()

    chats = ChatHistory.query.filter_by(
        username=user.name
    ).order_by(ChatHistory.id.desc()).all()

    return render_template(
        "chat_history.html",
        chats=chats
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

    percentage = round((score / len(dynamic_answers)) * 100)

    return render_template(
    "result.html",
    score=score,
    total=len(dynamic_answers),
    percentage=percentage
)
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