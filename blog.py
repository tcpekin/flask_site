import sys
from flask import Flask, render_template, request
from flask.helpers import redirect, url_for
from flask_flatpages import FlatPages, pygments_style_defs

# from flask_frozen import Freezer

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = ".md"
FLATPAGES_ROOT = "content"
POST_DIR = "posts"

app = Flask(__name__)
flatpages = FlatPages(app)
# freezer = Freezer(app)
app.config.from_object(__name__)


@app.route("/")
def index():

    return render_template("index.html")


@app.route("/about")
def about():
    content = flatpages.get_or_404("about")
    print("Hello world!")
    # content='1'
    return render_template("about.html", content=content)


@app.route("/test/", methods=['GET','POST'])
def test():
    success=False
    nm=None
    if request.method == "POST":
        try:
            nm = request.form['nm']
            success=True
            print(nm)
        except:
            print('Stop trying to break the site.')
        return redirect(url_for('test'))
    print(success)
    return render_template("test.html", success=success, nm=nm)


@app.route("/posts/")
def posts():
    posts = [p for p in flatpages if p.path.startswith(POST_DIR)]
    posts.sort(key=lambda item: item["date"], reverse=False)
    return render_template("posts.html", posts=posts)


@app.route("/posts/<name>/")
def post(name):
    path = "{}/{}".format(POST_DIR, name)
    print(path + "hkhk", file=sys.stderr)
    post = flatpages.get_or_404(path)
    return render_template("post.html", post=post)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        # freezer.freeze()
        pass
    else:
        app.run(host="0.0.0.0", debug=True)
