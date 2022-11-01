from typing import Iterable
import random

from music.domainmodel.track import Track
from music.adapters.repository import AbstractRepository


def get_genre_names(repo: AbstractRepository):
    genres = list(repo.get_genres())
    genre_names = [genre.name for genre in genres]
    return genre_names


def get_artist_names(repo: AbstractRepository):
    artists = list(repo.get_artists())
    artist_names = [artist.full_name for artist in artists]
    return artist_names


def get_random_tracks(quantity, repo: AbstractRepository):
    track_count = len(repo.get_tracks())

    if quantity >= track_count:
        # Reduce the quantity of ids to generate if the repository has an insufficient number of articles.
        quantity = track_count - 1

    # Pick distinct and random articles.
    random_ids = random.sample(range(1, track_count), quantity)
    t = repo.get_random_tracks_by_id(random_ids, quantity)

    return t


def track_to_dict(track: Track):
    track_dict = {
        'title': track.title,
        'duration': track.track_duration,
        'id': track.track_id
    }
    return track_dict


def tracks_to_dict(tracks: Iterable[Track]):
    return [track_to_dict(track) for track in tracks]


def tracks(repo: AbstractRepository):
    return repo.get_tracks()
