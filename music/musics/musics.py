from flask import Blueprint
from flask import request, render_template, redirect, url_for, session

from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

import music.adapters.repository as repo
import music.utilities.utilities as utilities
import music.musics.services as services

from music.authentication.authentication import login_required


# Configure Blueprint.
musics_blueprint = Blueprint(
    'musics_bp', __name__)


@musics_blueprint.route('/tracks_by_artist', methods=['GET'])
def tracks_by_artist():
    # Read query parameters.
    target_name = request.args.get('artist')
    track_to_show_reviews = request.args.get('view_reviews_for')
    # Fetch the first and last articles in the series.
    first_track = services.get_first_track(repo.repo_instance)
    last_track = services.get_last_track(repo.repo_instance)
    reviews = services.reviews(repo.repo_instance)
    reviews_id = services.reviews_id(reviews)
    if target_name is None:
        # No date query parameter, so return articles from day 1 of the series.
        target_name = first_track['artist'].full_name

    if track_to_show_reviews is None:
        # No view-comments query parameter, so set to a non-existent article id.
        track_to_show_reviews = -1
    else:
        # Convert article_to_show_comments from string to int.
        track_to_show_reviews = int(track_to_show_reviews)
    # Fetch article(s) for the target date. This call also returns the previous and next dates for articles immediately
    # before and after the target date.
    tracks, previous_name, next_name = services.get_tracks_by_name(target_name, repo.repo_instance)

    first_track_url = None
    last_track_url = None
    next_track_url = None
    prev_track_url = None

    if len(tracks) > 0:
        # There's at least one article for the target date.
        if previous_name is not None:
            # There are articles on a previous date, so generate URLs for the 'previous' and 'first' navigation buttons.
            prev_track_url = url_for('musics_bp.tracks_by_artist', artist=previous_name)
            first_track_url = url_for('musics_bp.tracks_by_artist', artist=first_track['artist'].full_name)

        # There are articles on a subsequent date, so generate URLs for the 'next' and 'last' navigation buttons.
        if next_name is not None:
            next_track_url = url_for('musics_bp.tracks_by_artist', artist=next_name)
            last_track_url = url_for('musics_bp.tracks_by_artist', artist=last_track['artist'].full_name)

        for track in tracks:
            track['view_review_url'] = url_for('musics_bp.tracks_by_artist', artist=target_name, view_reviews_for=track['track_id'])
            track['add_review_url'] = url_for('musics_bp.review_on_track', track=track['track_id'])

        # Generate the webpage to display the articles.
        return render_template(
            'musics/tracks.html',
            title='Tracks',
            tracks_title=target_name,
            tracks=tracks,
            reviews=reviews,
            reviews_id=reviews_id,
            selected_tracks=utilities.get_selected_tracks(len(tracks) * 2),
            genre_urls=utilities.get_genres_and_urls(),
            first_track_url=first_track_url,
            last_track_url=last_track_url,
            prev_track_url=prev_track_url,
            next_track_url=next_track_url,
            show_reviews_for_track=track_to_show_reviews,
            artist_urls=utilities.get_artists_and_urls()
        )

    # No articles to show, so return the homepage.
    return redirect(url_for('home_bp.home'))


@musics_blueprint.route('/tracks_by_genre', methods=['GET'])
def tracks_by_genre():
    tracks_per_page = 5

    # Read query parameters.
    genre_name = request.args.get('genre')
    cursor = request.args.get('cursor')
    track_to_show_reviews = request.args.get('view_reviews_for')
    reviews = services.reviews(repo.repo_instance)
    reviews_id = services.reviews_id(reviews)
    if track_to_show_reviews is None:
        # No view-comments query parameter, so set to a non-existent article id.
        track_to_show_reviews = -1
    else:
        # Convert article_to_show_comments from string to int.
        track_to_show_reviews = int(track_to_show_reviews)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve article ids for articles that are tagged with tag_name.
    track_ids = services.get_track_ids_for_genre(genre_name, repo.repo_instance)

    # Retrieve the batch of articles to display on the Web page.
    tracks = services.get_tracks_by_id(track_ids[cursor:cursor + tracks_per_page], repo.repo_instance)

    first_track_url = None
    last_track_url = None
    next_track_url = None
    prev_track_url = None

    if cursor > 0:
        # There are preceding articles, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_track_url = url_for('musics_bp.tracks_by_genre', genre=genre_name, cursor=cursor - tracks_per_page)
        first_track_url = url_for('musics_bp.tracks_by_genre', genre=genre_name)

    if cursor + tracks_per_page < len(track_ids):
        # There are further articles, so generate URLs for the 'next' and 'last' navigation buttons.
        next_track_url = url_for('musics_bp.tracks_by_genre', genre=genre_name, cursor=cursor + tracks_per_page)

        last_cursor = tracks_per_page * int(len(track_ids) / tracks_per_page)
        if len(track_ids) % tracks_per_page == 0:
            last_cursor -= tracks_per_page
        last_track_url = url_for('musics_bp.tracks_by_genre', genre=genre_name, cursor=last_cursor)

    for track in tracks:
        track['view_review_url'] = url_for('musics_bp.tracks_by_genre', genre=genre_name, cursor=cursor, view_reviews_for=track['track_id'])
        track['add_review_url'] = url_for('musics_bp.review_on_track', track=track['track_id'])

    # Generate the webpage to display the articles.
    return render_template(
        'musics/tracks.html',
        title='Tracks',
        tracks_title='Tracks with the Genre: ' + genre_name,
        tracks=tracks,
        reviews=reviews,
        reviews_id=reviews_id,
        selected_tracks=utilities.get_selected_tracks(len(tracks) * 2),
        genre_urls=utilities.get_genres_and_urls(),
        first_track_url=first_track_url,
        last_track_url=last_track_url,
        prev_track_url=prev_track_url,
        next_track_url=next_track_url,
        show_reviews_for_track=track_to_show_reviews,
        artist_urls=utilities.get_artists_and_urls()
    )


@musics_blueprint.route('/review', methods=['GET', 'POST'])
@login_required
def review_on_track():
    # Obtain the user name of the currently logged in user.
    user_name = session['user_name']
    reviews = services.reviews(repo.repo_instance)
    reviews_id = services.reviews_id(reviews)
    # Create form. The form maintains state, e.g. when this method is called with a HTTP GET request and populates
    # the form with an article id, when subsequently called with a HTTP POST request, the article id remains in the
    # form.
    form = ReviewForm()
    if form.validate_on_submit():
        # Successful POST, i.e. the comment text has passed data validation.
        # Extract the article id, representing the commented article, from the form.
        track_id = int(form.track_id.data)

        # Use the service layer to store the new comment.
        services.add_review(track_id, form.review.data, user_name, repo.repo_instance)

        # Retrieve the article in dict form.
        track = services.get_track(track_id, repo.repo_instance)
        # Cause the web browser to display the page of all articles that have the same date as the commented article,
        # and display all comments, including the new comment.
        return redirect(url_for('musics_bp.tracks_by_artist', artist=track['artist'].full_name, view_reviews_for=track_id))

    if request.method == 'GET':
        # Request is a HTTP GET to display the form.
        # Extract the article id, representing the article to comment, from a query parameter of the GET request.
        track_id = int(request.args.get('track'))

        # Store the article id in the form.
        form.track_id.data = track_id
    else:
        # Request is a HTTP POST where form validation has failed.
        # Extract the article id of the article being commented from the form.
        track_id = int(form.track_id.data)

    # For a GET or an unsuccessful POST, retrieve the article to comment in dict form, and return a Web page that allows
    # the user to enter a comment. The generated Web page includes a form object.
    track = services.get_track(track_id, repo.repo_instance)
    return render_template(
        'musics/review_on_track.html',
        title='Edit track',
        track=track,
        form=form,
        reviews=reviews,
        reviews_id=reviews_id,
        handler_url=url_for('musics_bp.review_on_track'),
        selected_tracks=utilities.get_selected_tracks(),
        genre_urls=utilities.get_genres_and_urls(),
        artist_urls=utilities.get_artists_and_urls()
    )


class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)


class ReviewForm(FlaskForm):
    review = TextAreaField('Review', [
        DataRequired(),
        Length(min=4, message='Your comment is too short'),
        ProfanityFree(message='Your comment must not contain profanity')])
    track_id = HiddenField("Track id")
    submit = SubmitField('Submit')