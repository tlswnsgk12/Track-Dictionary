import os
import csv
import ast
import random
from pathlib import Path
from typing import List

from werkzeug.security import generate_password_hash

from bisect import bisect, bisect_left, insort_left
from music.adapters.repository import AbstractRepository, RepositoryException
from music.domainmodel.artist import Artist
from music.domainmodel.album import Album
from music.domainmodel.genre import Genre
from music.domainmodel.review import Review
from music.domainmodel.track import Track
from music.domainmodel.user import User

data_path = Path('music') / 'adapters' / 'data'


class MemoryRepository(AbstractRepository):
    # Articles ordered by date, not id. id is assumed unique.

    def __init__(self):
        self.__tracks = list()
        self.__tracks_index = dict()
        self.__artists = set()
        self.__albums = set()
        self.__genres = set()
        self.__users = list()
        self.__reviews = list()
        self.__dup_artists = list()

    def add_user(self, user: User):
        self.__users.append(user)

    def get_user(self, user_name) -> User:
        return next((user for user in self.__users if user.user_name == user_name), None)

    def add_track(self, track: Track):
        insort_left(self.__tracks, track)
        self.__tracks_index[track.track_id] = track

    def get_tracks(self):
        return self.__tracks

    def get_track(self, id: int) -> Track:
        track = None

        try:
            track = self.__tracks_index[id]
        except KeyError:
            pass  # Ignore exception and return None.

        return track

    def get_tracks_by_name(self, target_name) -> List[Track]:
        matching_tracks = list()
        for track in self.__tracks:
            if track.artist.full_name == target_name:
                matching_tracks.append(track)

        return matching_tracks

    def get_number_of_tracks(self):
        return len(self.__tracks)

    def get_first_track(self):
        track = None

        if len(self.__tracks) > 0:
            track = self.__tracks[0]
        return track

    def get_last_track(self):
        track = None

        if len(self.__tracks) > 0:
            track = self.__tracks[-1]
        return track

    def get_tracks_by_id(self, id_list):
        # Strip out any ids in id_list that don't represent Article ids in the repository.
        existing_ids = [id for id in id_list if id in self.__tracks_index]

        # Fetch the Articles.
        tracks = [self.__tracks_index[id] for id in existing_ids]
        return tracks

    def get_random_tracks_by_id(self, id_list, quantity):
        tracks = []
        while len(tracks) != len(id_list):
            for track in self.__tracks:
                if track.track_id in id_list:
                    tracks.append(track)
                if len(tracks) == quantity:
                    break
            id_list = random.sample(range(1, len(self.__tracks)), quantity)
        return tracks

    def get_track_ids_for_genre(self, genre_name: str):
        # Linear search, to find the first occurrence of a Tag with the name tag_name.
        genre = next((genre for genre in self.__genres if genre.name == genre_name), None)
        tracks = list()
        for track in self.__tracks:
            for genre in track.genres:
                if genre.name == genre_name:
                    tracks.append(track)
        # Retrieve the ids of articles associated with the Tag.
        if genre is not None:
            track_ids = [track.track_id for track in tracks]
        else:
            # No Tag with name tag_name, so return an empty list.
            track_ids = list()
        return track_ids

    def get_name_of_previous_track(self, track: Track):
        previous_name = None

        try:
            index = self.track_index(track)
            for stored_track in reversed(self.__tracks[0:index]):
                if stored_track.track_id < track.track_id:
                    previous_name = stored_track.artist.full_name
                    break
        except ValueError:
            # No earlier articles, so return None.
            pass

        return previous_name

    def get_name_of_next_track(self, track: Track):
        next_name = None
        self.__dup_artists = list()

        try:
            index = self.track_index(track)
            for track in self.__tracks[:index]:
                self.__dup_artists.append(track.artist.full_name)
            for stored_track in self.__tracks[index + 1:len(self.__tracks)]:
                if stored_track.track_id > track.track_id and stored_track.artist.full_name in self.__dup_artists:
                    pass
                elif stored_track.track_id > track.track_id:
                    next_name = stored_track.artist.full_name
                    break
        except ValueError:
            # No subsequent articles, so return None.
            pass

        return next_name

    def add_genre(self, genre: Genre):
        self.__genres.add(genre)

    def get_genres(self):
        return self.__genres

    def add_review(self, review: Review):
        # call parent class first, add_comment relies on implementation of code common to all derived classes
        super().add_review(review)
        self.__reviews.append(review)

    def get_reviews(self):
        return self.__reviews

    def reset_tracks(self):
        self.__tracks = []

    def get_artists(self):
        return self.__artists

    def add_artist(self, artist: Artist):
        self.__artists.add(artist)

    def get_albums(self):
        return self.__albums

    def add_album(self, album: Album):
        self.__albums.add(album)

    def track_index(self, track: Track):
        t = True
        index = bisect_left(self.__tracks, track)
        if index != len(self.__tracks) and self.__tracks[index].title == track.title:
            while t:
                if index == len(self.__tracks) - 1:
                    break
                if track.artist.full_name == self.__tracks[index + 1].artist.full_name:
                    index += 1
                else:
                    break
            return index
        raise ValueError


def create_track_object(track_row):
    track = Track(int(track_row['track_id']), track_row['track_title'])
    track.track_url = track_row['track_url']
    track_duration = round(float(
        track_row['track_duration'])) if track_row['track_duration'] is not None else None
    if type(track_duration) is int:
        track.track_duration = track_duration
    return track


def create_artist_object(track_row):
    artist_id = int(track_row['artist_id'])
    artist = Artist(artist_id, track_row['artist_name'])
    return artist


def create_album_object(row):
    album_id = int(row['album_id'])
    album = Album(album_id, row['album_title'])
    album.album_url = row['album_url']
    album.album_type = row['album_type']

    album.release_year = int(
        row['album_year_released']) if row['album_year_released'].isdigit() else None

    return album


def extract_genres(track_row: dict):
    # List of dictionaries inside the string.
    track_genres_raw = track_row['track_genres']
    # Populate genres. track_genres can be empty (None)
    genres = []
    if track_genres_raw:
        try:
            genre_dicts = ast.literal_eval(
                track_genres_raw) if track_genres_raw != "" else []

            for genre_dict in genre_dicts:
                genre = Genre(
                    int(genre_dict['genre_id']), genre_dict['genre_title'])
                genres.append(genre)
        except Exception as e:
            print(track_genres_raw)
            print(f'Exception occurred while parsing genres: {e}')

    return genres


def read_albums_file_as_dict(filename: str):
    if not os.path.exists(filename):
        print(f"path {filename} does not exist!")

    album_dict = dict()
    # encoding of unicode_escape is required to decode successfully
    with open(filename, encoding="unicode_escape") as album_csv:
        reader = csv.DictReader(album_csv)
        for row in reader:
            album_id = int(
                row['album_id']) if row['album_id'].isdigit() else row['album_id']
            if type(album_id) is not int:
                print(f'Invalid album_id: {album_id}')
                print(row)
                continue
            album = create_album_object(row)
            album_dict[album_id] = album

    return album_dict


def read_tracks_file(filename: str):
    if not os.path.exists(filename):
        print(f"path {filename} does not exist!")
        return
    track_rows = []
    # encoding of unicode_escape is required to decode successfully
    with open(filename, encoding='unicode_escape') as track_csv:
        reader = csv.DictReader(track_csv)
        for track_row in reader:
            track_rows.append(track_row)
    return track_rows


def read_csv_files(data_path: Path, repo: MemoryRepository):
    album_filename = str(data_path / "raw_albums_excerpt.csv")
    track_filename = str(data_path / "raw_tracks_excerpt.csv")
    # key is album_id
    albums_dict: dict = read_albums_file_as_dict(album_filename)
    # list of track csv rows, not track objects
    track_rows: list = read_tracks_file(track_filename)

    # Make sure re-initialize to empty list, so that calling this function multiple times does not create
    # duplicated dataset.
    repo.reset_tracks()
    for track_row in track_rows:
        track = create_track_object(track_row)
        artist = create_artist_object(track_row)
        track.artist = artist

        # Extract track_genres attributes and assign genres to the track.
        track_genres = extract_genres(track_row)
        for genre in track_genres:
            track.add_genre(genre)

        album_id = int(
            track_row['album_id']) if track_row['album_id'].isdigit() else None

        album = albums_dict[album_id] if album_id in albums_dict else None
        track.album = album

        # Populate datasets for Artist and Genre
        if artist not in repo.get_artists():
            repo.add_artist(artist)

        if album is not None and album not in repo.get_albums():
            repo.add_album(album)

        for genre in track_genres:
            if genre not in repo.get_genres():
                repo.add_genre(genre)

        repo.add_track(track)
    return repo.get_tracks()
