import pytest

from flask import session


def test_logout(client, auth):
    # Login a user.
    auth.login()

    with client:
        # Check that logging out clears the user's session.
        auth.logout()
        assert 'user_id' not in session


def test_index(client):
    # Check that we can retrieve the home page.
    response = client.get('/')
    assert response.status_code == 200
    assert b'Track' in response.data


def test_login_required_to_comment(client):
    response = client.post('/review')
    assert response.headers['Location'] == '/authentication/login'


def test_tracks_without_artist(client):
    # Check that we can retrieve the articles page.
    response = client.get('/tracks_by_artist')
    assert response.status_code == 200

    # Check that without providing a date query parameter the page includes the first article.
    assert b'Abominog' in response.data
    assert b'Peel Back The Mountain Sky' in response.data


def test_tracks_with_artist(client):
    # Check that we can retrieve the articles page.
    response = client.get('/tracks_by_artist?artist=AWOL')
    assert response.status_code == 200

    # Check that all articles on the requested date are included on the page.
    assert b'AWOL' in response.data
    assert b'Food' in response.data


def test_tracks_with_genre(client):
    # Check that we can retrieve the articles page.
    response = client.get('/tracks_by_genre?genre=Blues')
    assert response.status_code == 200

    # Check that all articles tagged with 'Health' are included on the page.
    assert b'Tracks with the Genre: Blues' in response.data
    assert b'Interview' in response.data