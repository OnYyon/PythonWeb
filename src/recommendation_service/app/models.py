from .database import db
import uuid


class Genre(db.Model):  # type: ignore[unsupported-base]
    __tablename__ = "genres"

    uuid = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)


class Film(db.Model):  # type: ignore[unsupported-base]
    __tablename__ = "films"

    uuid = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    release_date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    poster_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    genres = db.relationship("Genre", secondary="film_genres", backref="films")


class FilmGenre(db.Model):  # type: ignore[unsupported-base]
    __tablename__ = "film_genres"

    id = db.Column(db.BigInteger, primary_key=True)
    film_id = db.Column(db.Uuid, db.ForeignKey("films.uuid"), nullable=False)
    genre_id = db.Column(db.Uuid, db.ForeignKey("genres.uuid"), nullable=False)


class Watchlist(db.Model):  # type: ignore[unsupported-base]
    __tablename__ = "watchlist"

    uuid = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    user_uuid = db.Column(db.Uuid, nullable=False)
    film_id = db.Column(db.Uuid, db.ForeignKey("films.uuid"), nullable=False)
    added_at = db.Column(db.DateTime, nullable=False)

    film = db.relationship("Film")
