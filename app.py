from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from database import db
from models import Board, Thumbnail
import re
import os

app = Flask(__name__)
CORS(app)

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'thumbnails.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# ---------------- Helper ----------------
def extract_youtube_id(url: str):
    """Extract YouTube video ID and return maxres thumbnail URL"""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if not match:
        return None
    video_id = match.group(1)
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

# ---------------- Routes ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/boards", methods=["GET", "POST"])
def boards():
    if request.method == "POST":
        data = request.get_json()
        board = Board(name=data.get("name"))
        db.session.add(board)
        db.session.commit()
        return jsonify({"id": board.id, "name": board.name, "thumbnails": []}), 201

    all_boards = Board.query.all()
    return jsonify([
        {
            "id": b.id,
            "name": b.name,
            "thumbnails": [{"id": t.id, "url": t.url, "title": t.title} for t in b.thumbnails]
        } for b in all_boards
    ])

@app.route("/api/boards/<int:board_id>", methods=["DELETE", "PUT"])
def board_detail(board_id):
    board = Board.query.get_or_404(board_id)

    if request.method == "DELETE":
        db.session.delete(board)
        db.session.commit()
        return jsonify({"message": "Board deleted"})

    if request.method == "PUT":
        data = request.get_json()
        board.name = data.get("name", board.name)
        db.session.commit()
        return jsonify({"id": board.id, "name": board.name})

@app.route("/api/boards/<int:board_id>/thumbnails", methods=["POST"])
def add_thumbnail(board_id):
    board = Board.query.get_or_404(board_id)
    data = request.get_json()
    yt_url = data.get("url")
    thumb_url = extract_youtube_id(yt_url) or yt_url
    thumbnail = Thumbnail(
        title=data.get("title", "Untitled"),
        url=thumb_url,
        board=board
    )
    db.session.add(thumbnail)
    db.session.commit()
    return jsonify({"id": thumbnail.id, "url": thumbnail.url, "title": thumbnail.title}), 201

@app.route("/api/thumbnails/<int:thumb_id>", methods=["DELETE"])
def delete_thumbnail(thumb_id):
    thumb = Thumbnail.query.get_or_404(thumb_id)
    db.session.delete(thumb)
    db.session.commit()
    return jsonify({"message": "Thumbnail deleted"})

# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=True)
