from flask import Flask, request, render_template, redirect, url_for, session, jsonify, flash
import pandas as pd
import random
import json
from flask_sqlalchemy import SQLAlchemy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = "shopwiz_secret_2024_ultrakey"

# ── Database ──────────────────────────────────────────────────────────────────
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ecom.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email    = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)


class Wishlist(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, nullable=False)
    prod_name= db.Column(db.String(300), nullable=False)


with app.app_context():
    db.create_all()

# ── Load Data ─────────────────────────────────────────────────────────────────
trending_products = pd.read_csv("models/trending_products.csv")
train_data        = pd.read_csv("models/clean_data.csv")

LOCAL_IMAGES = [
    "img/img_1.png", "img/img_2.png", "img/img_3.png", "img/img_4.png",
    "img/img_5.png", "img/img_6.png", "img/img_7.png", "img/img_8.png",
]
PRICES = [29.99, 39.99, 49.99, 59.99, 79.99, 99.99, 119.99, 149.99]
CATEGORIES = ["Beauty", "Health", "Skin Care", "Hair Care", "Supplements",
               "Personal Care", "Vitamins", "Fragrance"]


def truncate(text, length=30):
    return str(text)[:length] + "..." if len(str(text)) > length else str(text)

# Register as a Jinja2 filter so all templates can use it without passing explicitly
app.jinja_env.filters['truncate_name'] = truncate
app.jinja_env.globals['truncate'] = truncate


def enrich(df):
    """Attach random local image, price, category to a DataFrame slice."""
    records = df.to_dict(orient="records")
    for r in records:
        r["local_img"] = random.choice(LOCAL_IMAGES)
        r["price"]     = random.choice(PRICES)
        r["category"]  = random.choice(CATEGORIES)
        r["discount"]  = random.choice([0, 10, 15, 20, 25])
        r["Name"]      = str(r.get("Name", ""))
        r["Brand"]     = str(r.get("Brand", ""))
        r["Rating"]    = r.get("Rating", 4.0)
        r["ReviewCount"] = r.get("ReviewCount", 0)
    return records


def content_based_recommendations(item_name, top_n=8):
    if item_name not in train_data['Name'].values:
        return []
    tfidf = TfidfVectorizer(stop_words='english')
    matrix = tfidf.fit_transform(train_data['Tags'])
    sim = cosine_similarity(matrix, matrix)
    idx = train_data[train_data['Name'] == item_name].index[0]
    scores = sorted(list(enumerate(sim[idx])), key=lambda x: x[1], reverse=True)
    top_idx = [x[0] for x in scores[1:top_n+1]]
    return enrich(train_data.iloc[top_idx][['Name','ReviewCount','Brand','ImageURL','Rating']])


# ── Home ──────────────────────────────────────────────────────────────────────
@app.route("/")
@app.route("/index")
def index():
    trending = enrich(trending_products.head(8))
    featured = enrich(train_data.sample(4))
    user = session.get("username")
    return render_template("index.html", trending=trending, featured=featured,
                           truncate=truncate, user=user, categories=CATEGORIES)


# ── Products ──────────────────────────────────────────────────────────────────
@app.route("/products")
def products():
    page      = int(request.args.get("page", 1))
    category  = request.args.get("category", "")
    sort      = request.args.get("sort", "")
    per_page  = 12
    data      = train_data.copy()

    if category:
        # filter by rough keyword match in Tags
        data = data[data['Tags'].str.contains(category.lower(), case=False, na=False)]

    if sort == "low":
        data = data.sample(frac=1)   # randomised (no real price col)
    elif sort == "high":
        data = data.sample(frac=1)
    elif sort == "rating":
        data = data.sort_values("Rating", ascending=False)

    total  = len(data)
    start  = (page - 1) * per_page
    items  = enrich(data.iloc[start:start+per_page][['Name','ReviewCount','Brand','ImageURL','Rating']])
    pages  = (total // per_page) + (1 if total % per_page else 0)
    user   = session.get("username")
    return render_template("products.html", items=items, truncate=truncate,
                           page=page, pages=pages, category=category, sort=sort,
                           categories=CATEGORIES, user=user)


# ── Product Detail ────────────────────────────────────────────────────────────
@app.route("/product/<path:name>")
def product_detail(name):
    row = train_data[train_data['Name'] == name]
    if row.empty:
        flash("Product not found.", "error")
        return redirect(url_for("products"))
    product   = enrich(row[['Name','ReviewCount','Brand','ImageURL','Rating']])[0]
    similar   = content_based_recommendations(name, top_n=4)
    user      = session.get("username")
    return render_template("product_detail.html", product=product,
                           similar=similar, truncate=truncate, user=user)


# ── Recommendations ───────────────────────────────────────────────────────────
@app.route("/recommendations", methods=["GET", "POST"])
def recommendations():
    recs    = []
    message = ""
    prod    = ""
    if request.method == "POST":
        prod = request.form.get("prod", "").strip()
        nbr  = int(request.form.get("nbr", 8))
        recs = content_based_recommendations(prod, top_n=nbr)
        if not recs:
            message = f"No recommendations found for '{prod}'. Try a different product name."
    user = session.get("username")
    return render_template("recommendations.html", recs=recs, message=message,
                           prod=prod, truncate=truncate, user=user)


# ── Auth ──────────────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["username"] = user.username
            session["user_id"]  = user.id
            flash("Welcome back, " + user.username + "! 👋", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials. Please try again.", "error")
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email    = request.form["email"]
        password = request.form["password"]
        existing = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing:
            flash("Username or email already exists.", "error")
        else:
            db.session.add(User(username=username, email=email, password=password))
            db.session.commit()
            session["username"] = username
            flash("Account created! Welcome, " + username + "! 🎉", "success")
            return redirect(url_for("index"))
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You've been logged out.", "info")
    return redirect(url_for("index"))


# ── API: Search suggestions ───────────────────────────────────────────────────
@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip().lower()
    if len(q) < 2:
        return jsonify([])
    results = train_data[train_data['Name'].str.lower().str.contains(q, na=False)]['Name'].head(8).tolist()
    return jsonify(results)


# ── API: Wishlist ─────────────────────────────────────────────────────────────
@app.route("/api/wishlist/toggle", methods=["POST"])
def wishlist_toggle():
    if "user_id" not in session:
        return jsonify({"status": "login_required"}), 401
    data = request.get_json()
    name = data.get("name", "")
    existing = Wishlist.query.filter_by(user_id=session["user_id"], prod_name=name).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"status": "removed"})
    else:
        db.session.add(Wishlist(user_id=session["user_id"], prod_name=name))
        db.session.commit()
        return jsonify({"status": "added"})


@app.route("/wishlist")
def wishlist():
    if "user_id" not in session:
        return redirect(url_for("login"))
    items_db = Wishlist.query.filter_by(user_id=session["user_id"]).all()
    names    = [w.prod_name for w in items_db]
    rows     = train_data[train_data['Name'].isin(names)]
    items    = enrich(rows[['Name','ReviewCount','Brand','ImageURL','Rating']]) if not rows.empty else []
    return render_template("wishlist.html", items=items, truncate=truncate,
                           user=session.get("username"))


# ── Main (legacy redirect) ────────────────────────────────────────────────────
@app.route("/main")
def main():
    return redirect(url_for("recommendations"))


if __name__ == "__main__":
    app.run(debug=True)