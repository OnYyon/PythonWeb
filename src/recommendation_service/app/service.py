from sqlalchemy import desc
from .database import db
from .models import Watchlist, Film, Genre

def get_recommendations(user_id: str) -> list:
    user_watchlist = Watchlist.query.filter_by(user_uuid=user_id).all()
    watched_film_ids = [w.film_id for w in user_watchlist]

    if not watched_film_ids:
        newest_films = Film.query.order_by(desc(Film.release_date)).limit(10).all()
        return _serialize_films(newest_films)

    favorite_genres = (
        db.session.query(Genre.uuid)
        .join(Film.genres)
        .filter(Film.uuid.in_(watched_film_ids))
        .distinct()
        .all()
    )
    genre_ids = [g[0] for g in favorite_genres]

    recommended_films = (
        Film.query.join(Film.genres)
        .filter(Genre.uuid.in_(genre_ids))
        .filter(~Film.uuid.in_(watched_film_ids))
        .distinct()
        .limit(10)
        .all()
    )

    if not recommended_films:
        fallback_films = Film.query.filter(~Film.uuid.in_(watched_film_ids)).order_by(desc(Film.release_date)).limit(10).all()
        return _serialize_films(fallback_films)

    return _serialize_films(recommended_films)

def _serialize_films(films: list) -> list:
    """Вспомогательная функция для превращения объектов SQLAlchemy в dict для JSON"""
    return [
        {
            "id": str(film.uuid),
            "title": film.title,
            "description": film.description,
            "release_date": film.release_date.isoformat() if film.release_date else None,
            "duration": film.duration,
            "poster_url": film.poster_url,
            "genres": [{"id": str(g.uuid), "name": g.name} for g in film.genres]
        }
        for film in films
    ]
