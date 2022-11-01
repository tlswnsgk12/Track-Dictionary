from datetime import date

import pytest

from music.authentication.services import AuthenticationException
from music.musics import services as musics_services
from music.authentication import services as auth_services
from music.musics.services import NonExistentTrackException


def test_can_add_user(in_memory_repo):
    new_user_name = 'jz'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)

    user_as_dict = auth_services.get_user(new_user_name, in_memory_repo)
    assert user_as_dict['user_name'] == new_user_name
    assert user_as_dict['password'].startswith('pbkdf2:sha256:')


def test_cannot_add_user_with_existing_name(in_memory_repo):
    auth_services.add_user('thorke', 'abcd1A23', in_memory_repo)
    user_name = 'thorke'
    password = 'abcd1A23'

    with pytest.raises(auth_services.NameNotUniqueException):
        auth_services.add_user(user_name, password, in_memory_repo)


def test_authentication_with_valid_credentials(in_memory_repo):
    new_user_name = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)

    try:
        auth_services.authenticate_user(new_user_name, new_password, in_memory_repo)
    except AuthenticationException:
        assert False


def test_authentication_with_invalid_credentials(in_memory_repo):
    new_user_name = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_user_name, new_password, in_memory_repo)

    with pytest.raises(auth_services.AuthenticationException):
        auth_services.authenticate_user(new_user_name, '0987654321', in_memory_repo)


def test_can_add_comment(in_memory_repo):
    auth_services.add_user('jz', 'iLdne23Ls', in_memory_repo)
    track_id = 3
    comment_text = 'The loonies are stripping the supermarkets bare!'
    user_name = 'jz'
    musics_services.add_review(track_id, comment_text, user_name, in_memory_repo)

    for review in musics_services.reviews(in_memory_repo):
        if review.review_text == comment_text:
            assert review.review_text == comment_text


def test_cannot_add_comment_for_non_existent_track(in_memory_repo):
    auth_services.add_user('fmercury', '1Aiila3sf3', in_memory_repo)
    article_id = 1900
    comment_text = "COVID-19 - what's that?"
    user_name = 'fmercury'
    with pytest.raises(musics_services.NonExistentTrackException):
        musics_services.add_review(article_id, comment_text, user_name, in_memory_repo)


def test_cannot_add_comment_by_unknown_user(in_memory_repo):
    article_id = 3
    comment_text = 'The loonies are stripping the supermarkets bare!'
    user_name = 'gmichael'
    with pytest.raises(musics_services.UnknownUserException):
        musics_services.add_review(article_id, comment_text, user_name, in_memory_repo)


def test_can_get_track(in_memory_repo):
    article_id = 1

    article_as_dict = musics_services.get_track(article_id, in_memory_repo)

    assert article_as_dict['track_id'] == article_id
    assert article_as_dict['title'] == "Father's Day"
    assert article_as_dict['artist'].full_name == 'Abominog'
    assert article_as_dict['track_url'] == 'http://freemusicarchive.org/music/Abominog/mp3_1_1535/Fathers_Day'
    assert article_as_dict['track_duration'] == 837

    tag_names = [dictionary['name'] for dictionary in article_as_dict['genres']]
    assert 'Loud-Rock' in tag_names


def test_cannot_get_track_with_non_existent_id(in_memory_repo):
    article_id = 1900
    with pytest.raises(musics_services.NonExistentTrackException):
        musics_services.get_track(article_id, in_memory_repo)


def test_get_first_track(in_memory_repo):
    article_as_dict = musics_services.get_first_track(in_memory_repo)

    assert article_as_dict['track_id'] == 1


def test_get_last_track(in_memory_repo):
    article_as_dict = musics_services.get_last_track(in_memory_repo)

    assert article_as_dict['track_id'] == 1855


def test_get_tracks_by_artist_with_one_artist(in_memory_repo):
    target_name = 'Abominog'

    tracks_as_dict, prev_name, next_name = musics_services.get_tracks_by_name(target_name, in_memory_repo)

    assert len(tracks_as_dict) == 2
    assert tracks_as_dict[0]['track_id'] == 1

    assert prev_name is None
    assert next_name == 'Adept'


def test_get_tracks_by_artist_with_non_existent_artist(in_memory_repo):
    target_name = 'testtest'

    articles_as_dict, prev_date, next_date = musics_services.get_tracks_by_name(target_name, in_memory_repo)

    assert len(articles_as_dict) == 0


def test_get_tracks_by_id(in_memory_repo):
    target_article_ids = [1, 2, 1900, 1901]
    articles_as_dict = musics_services.get_tracks_by_id(target_article_ids, in_memory_repo)
    assert len(articles_as_dict) == 2
    article_ids = [article['track_id'] for article in articles_as_dict]
    assert set([1, 2]).issubset(article_ids)