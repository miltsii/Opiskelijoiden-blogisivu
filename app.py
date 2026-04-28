from flask import Flask, request, redirect, render_template, session
from werkzeug.utils import secure_filename
import os
import re

from database.users import get_user_by_username, create_user, get_blog_name, check_password
from database.messages import get_messages, add_message, delete_message
from database.blogs import get_posts, get_all_posts, get_posts_by_user, add_post, delete_post
from database.comments import get_comments, get_comments_by_user_posts, add_comment
from database.categories import get_visit_count
from database.post_categories import init_db

app = Flask(__name__)
app.secret_key = "salainen"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def index():
    if "username" not in session:
        return redirect("/login")

    search = request.args.get("search")
    theme = request.args.get("theme")

    visits = get_visit_count()
    posts = get_posts(search=search)
    messages = get_messages(search=search, theme=theme)

    return render_template("index (1).html", visits=visits, messages=messages, posts=posts, session=session)


@app.route("/new")
def new():
    if "username" not in session:
        return redirect("/login")
    return render_template("new.html")


@app.route("/send", methods=["POST"])
def send():
    if "username" not in session:
        return redirect("/login")

    content = request.form["content"].strip()
    image = request.files.get("image")
    theme = request.form.get("theme")

    if content == "":
        return redirect("/new")

    image_path = None
    if image and image.filename != "":
        filename = secure_filename(image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)

    add_message(content, session["user_id"], theme, image_path)
    return redirect("/")


@app.route("/delete/<int:msg_id>", methods=["POST"])
def delete(msg_id):
    if "username" not in session:
        return redirect("/login")
    delete_message(msg_id, session["user_id"])
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    user = get_user_by_username(username)
    if user and check_password(user, password):
        session["user_id"] = user[0]
        session["username"] = username
        return redirect("/")
    else:
        return "Väärä käyttäjänimi tai salasana"


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/create_user", methods=["POST"])
def create_user_route():
    username = request.form["username"]
    blog_name = request.form["blog_name"]
    password = request.form["password"]
    password2 = request.form["password2"]

    if password != password2:
        return "Salasanat eivät täsmää. <a href='/register'>Yritä uudelleen</a>"
    if len(password) < 6:
        return "Salasanan pitää olla vähintään 6 merkkiä pitkä. <a href='/register'>Yritä uudelleen</a>"
    if not re.search(r"[a-zA-Z]", password) or not re.search(r"[0-9]", password):
        return "Salasanassa on oltava vähintään yksi kirjain ja yksi numero. <a href='/register'>Yritä uudelleen</a>"

    create_user(username, blog_name, password)
    return redirect("/login")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/post_new")
def post_new():
    if "username" not in session:
        return redirect("/login")
    return render_template("post.html")


@app.route("/post_send", methods=["POST"])
def post_send():
    if "username" not in session:
        return redirect("/login")

    title = request.form["title"].strip()
    content = request.form["content"].strip()
    image = request.files.get("image")
    theme = request.form.get("theme")
    image_path = None

    if image and image.filename != "":
        filename = secure_filename(image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)

    add_post(session["user_id"], title, content, theme, image_path)
    return redirect("/posts")


@app.route("/posts")
def posts():
    if "username" not in session:
        return redirect("/login")

    all_posts = get_all_posts()
    comments = get_comments()
    return render_template("posts.html", posts=all_posts, comments=comments)


@app.route("/post_delete/<int:post_id>", methods=["POST"])
def post_delete(post_id):
    if "username" not in session:
        return redirect("/login")
    delete_post(post_id, session["user_id"])
    return redirect("/posts")


@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):
    if "username" not in session:
        return redirect("/login")

    content = request.form["content"].strip()
    if content == "":
        return redirect("/posts")

    add_comment(post_id, session["user_id"], content)
    return redirect("/posts")


@app.route("/user/<username>")
def user_profile(username):
    if "username" not in session:
        return redirect("/login")

    posts = get_posts_by_user(username)
    blog_name = get_blog_name(username)
    comments = get_comments_by_user_posts(username)

    return render_template("user_profile.html",
                           posts=posts,
                           comments=comments,
                           username=username,
                           blog_name=blog_name)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)











