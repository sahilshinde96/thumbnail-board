from database import db

class Board(db.Model):
    __tablename__ = "boards"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    thumbnails = db.relationship("Thumbnail", backref="board", cascade="all, delete-orphan")

class Thumbnail(db.Model):
    __tablename__ = "thumbnails"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    url = db.Column(db.String(500), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey("boards.id"), nullable=False)