from flask import Blueprint, request, render_template, redirect, url_for, session

import music.adapters.repository as repo
import music.utilities.services as services

# Configure Blueprint.
utilities_blueprint = Blueprint(
    'utilities_bp', __name__)


def get_selected_tracks(quantity=3):
    tracks = services.get_random_tracks(quantity, repo.repo_instance)
    return tracks


def get_genres_and_urls():
    genre_names = services.get_genre_names(repo.repo_instance)
    genre_urls = dict()
    for genre_name in genre_names:
        genre_urls[genre_name] = url_for('musics_bp.tracks_by_genre', genre=genre_name)
    return genre_urls


def get_artists_and_urls():
    artist_names = services.get_artist_names(repo.repo_instance)
    artist_urls = dict()
    for artist_name in artist_names:
        artist_urls[artist_name] = url_for('musics_bp.tracks_by_artist', artist=artist_name)
    return artist_urls


def get_all_tracks():
    return services.tracks(repo.repo_instance)
