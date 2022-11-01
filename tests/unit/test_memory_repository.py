from datetime import date, datetime
from typing import List

import pytest

from music.domainmodel.album import Album
from music.domainmodel.artist import Artist
from music.domainmodel.genre import Genre
from music.domainmodel.playlist import PlayList
from music.domainmodel.review import Review
from music.domainmodel.track import Track
from music.domainmodel.user import User

from music.adapters.repository import RepositoryException


def test_repository_can_add_a_user(in_memory_repo):
    user = User('dave', '123456789')
    in_memory_repo.add_user(user)

    assert in_memory_repo.get_user('dave') is user


def test_repository_can_retrieve_a_user(in_memory_repo):
    user = User('jakm', '123456789')
    in_memory_repo.add_user(user)

    user = in_memory_repo.get_user('jakm')
    assert user == User('jakm', '123456789')


def test_repository_does_not_retrieve_a_non_existent_user(in_memory_repo):
    user = in_memory_repo.get_user('asdfasdfa')
    assert user is None


def test_repository_can_retrieve_track_count(in_memory_repo):
    number_of_tracks = in_memory_repo.get_number_of_tracks()
    assert number_of_tracks == 1855


def test_repository_can_add_track(in_memory_repo):
    track = Track(
        2020,
        'test'
    )
    in_memory_repo.add_track(track)

    assert in_memory_repo.get_track(2020) is track


def test_repository_can_retrieve_track(in_memory_repo):
    abc = Track(
        2021,
        'testtest'
    )
    in_memory_repo.add_track(abc)
    track = in_memory_repo.get_last_track()
    assert track.title == 'testtest'


def test_repository_does_not_retrieve_a_non_existent_track(in_memory_repo):
    track = in_memory_repo.get_track(9999)
    assert track is None


def test_repository_can_retrieve_tracks_by_artist(in_memory_repo):
    track = in_memory_repo.get_tracks_by_name("Abominog")
    assert len(track) == 2


def test_repository_does_not_retrieve_an_track_when_there_are_no_tracks_for_a_given_artist(in_memory_repo):
    track = in_memory_repo.get_tracks_by_name("asdfasdfasdf")
    assert len(track) == 0


def test_repository_can_retrieve_genres(in_memory_repo):
    genres: List[Genre] = in_memory_repo.get_genres()

    assert len(genres) == 55


def test_repository_can_get_first_track(in_memory_repo):
    track = in_memory_repo.get_first_track()
    assert track.title == "Father's Day"


def test_repository_can_get_last_track(in_memory_repo):
    track = in_memory_repo.get_last_track()
    assert track.title == '4'


def test_repository_can_get_tracks_by_ids(in_memory_repo):
    track = in_memory_repo.get_tracks_by_id([1, 2, 3])

    assert len(track) == 3
    assert track[
               0].title == "Father's Day"
    assert track[1].title == "Peel Back The Mountain Sky"
    assert track[2].title == 'Ed De Goem'


def test_repository_does_not_retrieve_track_for_non_existent_id(in_memory_repo):
    track = in_memory_repo.get_tracks_by_id([1, 8888])

    assert len(track) == 1
    assert track[
               0].title == "Father's Day"


def test_repository_returns_an_empty_list_for_non_existent_ids(in_memory_repo):
    track = in_memory_repo.get_tracks_by_id([0, 8463])

    assert len(track) == 0


def test_repository_returns_track_ids_for_existing_genre(in_memory_repo):
    track = in_memory_repo.get_track_ids_for_genre('Blues')
    gen = list()
    for id in track:
        track = in_memory_repo.get_track(id)
        for genre in track.genres:
            gen.append(genre.name)
    assert 'Blues' in gen


def test_repository_returns_an_empty_list_for_non_existent_genre(in_memory_repo):
    genres = in_memory_repo.get_track_ids_for_genre('abcdefg')

    assert len(genres) == 0


def test_repository_returns_date_of_previous_artist(in_memory_repo):
    track = in_memory_repo.get_track(2)
    previous_name = in_memory_repo.get_name_of_previous_track(track)

    assert previous_name == 'Abominog'


def test_repository_returns_none_when_there_are_no_previous_tracks(in_memory_repo):
    track = in_memory_repo.get_track(1)
    previous_name = in_memory_repo.get_name_of_previous_track(track)

    assert previous_name is None


def test_repository_returns_artist_of_next_track(in_memory_repo):
    track = in_memory_repo.get_track(1)
    next_artist = in_memory_repo.get_name_of_next_track(track)

    assert next_artist == 'Adept'


def test_repository_returns_none_when_there_are_no_subsequent_tracks(in_memory_repo):
    track = in_memory_repo.get_last_track()
    next_artist = in_memory_repo.get_name_of_next_track(track)

    assert next_artist is None


def test_repository_can_add_a_genre(in_memory_repo):
    genre = Genre(999, 'Motoring')
    in_memory_repo.add_genre(genre)

    assert genre in in_memory_repo.get_genres()


def test_repository_can_add_a_comment(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    track = in_memory_repo.get_track(2)
    comment = Review(user, track, "Trump's onto it!", 5)

    in_memory_repo.add_review(comment)

    assert comment in in_memory_repo.get_reviews()


def test_repository_can_retrieve_comments(in_memory_repo):
    assert len(in_memory_repo.get_reviews()) == 0



