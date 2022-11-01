from typing import List, Iterable
from datetime import date, datetime

from music.adapters.repository import AbstractRepository
from music.domainmodel.artist import Artist
from music.domainmodel.album import Album
from music.domainmodel.genre import Genre
from music.domainmodel.review import Review
from music.domainmodel.track import Track
from music.domainmodel.user import User


class NonExistentTrackException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def reviews(repo: AbstractRepository):
    return repo.get_reviews()


def reviews_id(review_list):
    ids = list()
    for review in review_list:
        ids.append(review.track.track_id)
    return ids


def make_review(comment_text: str, user: User, track: Track, rating: int):
    review = Review(user, track, comment_text, rating)
    user.add_review(review)
    track.add_review(review)

    return review


def add_review(track_id: int, comment_text: str, user_name: str, repo: AbstractRepository):
    # Check that the article exists.
    track = repo.get_track(track_id)
    if track is None:
        raise NonExistentTrackException

    user = repo.get_user(user_name)
    if user is None:
        raise UnknownUserException

    review = make_review(comment_text, user, track, 5)

    # Update the repository.
    repo.add_review(review)


def get_track(track_id: int, repo: AbstractRepository):
    track = repo.get_track(track_id)

    if track is None:
        raise NonExistentTrackException

    return track_to_dict(track)


def get_first_track(repo: AbstractRepository):
    track = repo.get_first_track()

    return track_to_dict(track)


def get_last_track(repo: AbstractRepository):
    track = repo.get_last_track()
    return track_to_dict(track)


def get_tracks_by_name(name, repo: AbstractRepository):
    # Returns articles for the target date (empty if no matches), the date of the previous article (might be null), the date of the next article (might be null)

    tracks = repo.get_tracks_by_name(name)

    tracks_dto = list()
    prev_name = next_name = None
    if len(tracks) > 0:
        prev_name = repo.get_name_of_previous_track(tracks[0])
        next_name = repo.get_name_of_next_track(tracks[0])

        # Convert Articles to dictionary form.
        tracks_dto = tracks_to_dict(tracks)

    return tracks_dto, prev_name, next_name


def get_track_ids_for_genre(genre_name, repo: AbstractRepository):
    track_ids = repo.get_track_ids_for_genre(genre_name)

    return track_ids


def get_tracks_by_id(id_list, repo: AbstractRepository):
    tracks = repo.get_tracks_by_id(id_list)

    # Convert Articles to dictionary form.
    tracks_as_dict = tracks_to_dict(tracks)

    return tracks_as_dict


def get_reviews_for_track(track_id, repo: AbstractRepository):
    track = repo.get_track(track_id)

    if track is None:
        raise NonExistentTrackException

    return review_to_dict(track.reviews)


# ============================================
# Functions to convert model entities to dicts
# ============================================

def track_to_dict(track: Track):
    track_dict = {
        'track_id': track.track_id,
        'title': track.title,
        'artist': track.artist,
        'album': track.album,
        'track_url': track.track_url,
        'track_duration': track.track_duration,
        'genres': genres_to_dict(track.genres)
    }
    return track_dict


def tracks_to_dict(tracks: Iterable[Track]):
    return [track_to_dict(track) for track in tracks]


def genre_to_dict(genre: Genre):
    genre_dict = {
        'name': genre.name,
        'genre_id': genre.genre_id
    }
    return genre_dict


def review_to_dict(review: Review):
    review_dict = {
        'user_name': review.user.user_name,
        'track_id': review.track.track_id,
        'comment_text': review.review_text,
        'timestamp': review.timestamp
    }
    return review_dict


def reviews_to_dict(reviews: Iterable[Review]):
    return [review_to_dict(review) for review in reviews]


def genres_to_dict(genres: Iterable[Genre]):
    return [genre_to_dict(genre) for genre in genres]


# ============================================
# Functions to convert dicts to model entities
# ============================================

def dict_to_track(dict):
    track = Track(dict.track_id, dict.title, dict.artist, dict.album, dict.track_url, dict.track_duration, dict.genres)
    # Note there's no comments or tags.
    return track
