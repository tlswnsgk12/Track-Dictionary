import pytest
import os

from music.domainmodel.artist import Artist
from music.domainmodel.track import Track
from music.domainmodel.genre import Genre
from music.domainmodel.review import Review
from music.domainmodel.album import Album
from music.domainmodel.user import User
from music.adapters.memory_repository import MemoryRepository, read_csv_files


class TestArtist:

    def test_construction(self):
        artist1 = Artist(1, 'Tailor Swift')
        assert str(artist1) == "<Artist Tailor Swift, artist id = 1>"
        artist2 = Artist(2, "Maroon 5")
        assert str(artist2) == '<Artist Maroon 5, artist id = 2>'
        artist3 = Artist(3, 'Kate Bush')
        assert str(artist3) == '<Artist Kate Bush, artist id = 3>'
        artist4 = Artist(4, ' Bad Bunny ')
        assert str(artist4) == '<Artist Bad Bunny, artist id = 4>'
        with pytest.raises(ValueError):
            Artist(None, 'Harry Styles')
        with pytest.raises(ValueError):
            Artist(-3, 'Harry Styles')
        artist5 = Artist(5, 2910)
        assert artist5.full_name is None

    def test_setters(self):
        artist1 = Artist(1, 'Tailor Swift')
        artist1.full_name = '  Tailor Fixed  '
        assert artist1.full_name == 'Tailor Fixed'
        assert str(artist1) == '<Artist Tailor Fixed, artist id = 1>'
        artist1.full_name = 32
        assert artist1.full_name is None
        assert artist1.full_name is None

    def test_equality(self):
        artist1 = Artist(1, 'Tailor Swift')
        artist2 = Artist(2, "Maroon 5")
        artist3 = Artist(3, 'Kate Bush')
        artist3_copy = Artist(3, 'Kate Bush')
        assert artist1 == artist1
        assert artist2 == artist2
        assert artist3 == artist3
        assert artist3 == artist3_copy
        assert artist1 != artist2
        assert artist1 != artist3
        assert artist2 != artist3
        assert artist1 != 'Tailor Swift'
        assert artist1 is not None

    def test_sorting(self):
        artist1 = Artist(2, 'Tailor Swift')
        artist2 = Artist(5, "Maroon 5")
        artist3 = Artist(8, 'Kate Bush')
        assert artist1 < artist2
        assert artist2 < artist3
        assert artist3 > artist1
        artist_list = [artist3, artist2, artist1]
        assert sorted(artist_list) == [artist1, artist2, artist3]

    def test_set(self):
        artist1 = Artist(1, 'Tailor Swift')
        artist2 = Artist(3, "Maroon 5")
        artist3 = Artist(8, 'Kate Bush')

        artist_set = set()
        artist_set.add(artist1)
        artist_set.add(artist2)
        artist_set.add(artist3)

        assert sorted(artist_set) == [artist1, artist2, artist3]

        # Test removal
        artist_set.discard(artist1)
        assert sorted(artist_set) == [artist2, artist3]


class TestGenre:

    def test_construction(self):
        genre1 = Genre(1, 'Jazz ')
        genre2 = Genre(2, ' Electronic ')

        assert str(genre1) == '<Genre Jazz, genre id = 1>'
        assert str(genre2) == '<Genre Electronic, genre id = 2>'

        # Test invalid id raises error
        with pytest.raises(ValueError):
            Genre('abc', 'Chill')

        # Test invalid id raises error
        with pytest.raises(ValueError):
            Genre(-30, 'Chill')

        # Construct with invalid name type sets it to None
        genre3 = Genre(3, 300)
        assert genre3.name is None

    def test_setters(self):
        genre1 = Genre(1, 'Jazz')

        assert genre1.genre_id == 1

        genre1.name = 'New Jazz'
        assert genre1.name == 'New Jazz'

        # Invalid type assignment sets name to None
        genre1.name = 100
        assert genre1.name is None

        # Empty string assignment sets name to None
        genre1.name = ''
        assert genre1.name is None

    def test_equality(self):
        genre1 = Genre(1, 'Jazz')
        genre2 = Genre(2, 'Electronic')
        genre3 = Genre(5, 'Electronic')

        assert genre1 == genre1
        assert genre1 != genre2
        assert genre2 != genre3

        assert genre1 != 'Jazz'
        assert genre2 != 105

    def test_sorting(self):
        genre1 = Genre(1, 'Jazz')
        genre2 = Genre(2, 'Electronic')
        genre3 = Genre(8, 'Latin')

        assert genre1 < genre2
        assert genre2 < genre3
        assert genre3 > genre1

        genre_list = [genre3, genre2, genre1]
        assert sorted(genre_list) == [genre1, genre2, genre3]

    def test_set(self):
        genre1 = Genre(1, 'Jazz')
        genre2 = Genre(2, 'Electronic')
        genre3 = Genre(8, 'Latin')

        genre_set = set()
        genre_set.add(genre1)
        genre_set.add(genre2)
        genre_set.add(genre3)

        assert sorted(genre_set) == [genre1, genre2, genre3]

        genre_set.discard(genre2)
        genre_set.discard(genre1)
        assert sorted(genre_set) == [genre3]


class TestAlbum:

    def test_construction(self):
        album1 = Album(15, 'Justice')
        album2 = Album(20, ' Planet Her ')

        assert str(album1) == '<Album Justice, album id = 15>'
        assert str(album2) == '<Album Planet Her, album id = 20>'

        # Test no id raises error
        with pytest.raises(ValueError):
            Album(None, 'Fine Line')

        # Test negative value of id raises error
        with pytest.raises(ValueError):
            Album(-3, 'Fine Line')

        # Test album title of wrong type sets title to None
        album3 = Album(3, 300)
        assert str(album3) == '<Album None, album id = 3>'

        album4 = Album(4, '')
        assert str(album4) == '<Album None, album id = 4>'

    def test_attributes(self):
        album1 = Album(15, 'Justice')

        with pytest.raises(AttributeError):
            album1.album_id = 2910

        # Test title getter & setter
        album1.title = ' Broken justice  '
        assert album1.title == 'Broken justice'

        album1.title = 1356
        assert album1.title is None
        album1.title = ''
        assert album1.title is None

        # Test album_url getter & setter
        album1.album_url = ' https://spotify/albums/15 '
        assert album1.album_url == 'https://spotify/albums/15'

        album1.album_url = float('inf')
        assert album1.album_url is None

        # Test album_type getter & setter
        album1.album_type = '  Live Performance '
        assert album1.album_type == 'Live Performance'

        album1.album_type = -10
        assert album1.album_type is None

        # Test release_year getter & setter
        album1.release_year = 2018
        assert album1.release_year == 2018

        album1.release_year = -2000
        assert album1.release_year is None

        album1.release_year = 2020.55
        assert album1.release_year is None

        album1.release_year = 'Invalid year'
        assert album1.release_year is None

    def test_equality(self):
        album1 = Album(15, 'Justice')
        album1_copy = Album(15, 'Justice')
        album2 = Album(20, 'Planet Her')
        album3 = Album(25, 'Rumours')

        assert album1 == album1
        assert album1 == album1_copy
        assert album1 != album2
        assert album1 != album3

        # Test changing the attribute does not affect the equality
        album1_copy.title = 'Something else'
        album1_copy.album_url = 'https://spotify/albums/2'
        assert album1 == album1_copy

    def test_sorting(self):
        album1 = Album(15, 'Justice')
        album2 = Album(20, 'Planet Her')
        album3 = Album(25, 'Rumours')

        assert album1 < album2
        assert album2 < album3

        album_list = [album2, album3, album2, album1, album3]
        assert sorted(album_list) == [album1, album2, album2, album3, album3]

    def test_set(self):
        album1 = Album(15, 'Justice')
        album2 = Album(20, 'Planet Her')
        album3 = Album(25, 'Rumours')

        album_set = set()
        album_set.add(album1)
        album_set.add(album2)
        album_set.add(album3)

        assert sorted(album_set) == [album1, album2, album3]

        album_set.remove(album1)
        album_set.remove(album2)
        assert list(album_set) == [album3]


class TestTrack:

    def test_construction(self):
        track1 = Track(1, 'As it Was ')
        track2 = Track(2, ' Heat Waves')
        track3 = Track(3, ' Tarot ')

        assert str(track1) == '<Track As it Was, track id = 1>'
        assert str(track2) == '<Track Heat Waves, track id = 2>'
        assert str(track3) == '<Track Tarot, track id = 3>'

        # Test if id of wrong type raises error
        with pytest.raises(ValueError):
            Track(None, 'Te Felicito')

        # Test negative value of id raises error
        with pytest.raises(ValueError):
            Track(-1, 'Te Felicito')

        # Setting title of wrong type sets title to None
        track4 = Track(5, 32)
        assert track4.title is None

    def test_attributes(self):
        track1 = Track(1, 'Shivers')

        # Test title setter
        track1.title = 'Fixed Shivers'
        assert track1.title == 'Fixed Shivers'

        # Title with trailing spaces
        track1.title = '  Fixed Shivers2   '
        assert track1.title == 'Fixed Shivers2'

        # Test tracK_url
        track1.track_url = ' https://spotify/track/1 '
        assert track1.track_url == 'https://spotify/track/1'

        # Test track duration
        track1.track_duration = 300
        assert track1.track_duration == 300

        artist = Artist(31, 'Justin Bieber')
        # Test artist attribute
        track1.artist = artist
        assert track1.artist == artist

        # Test album attribute
        album = Album(9289, 'Release Radar')

        # Assigning correct album type sets the attribute successfully
        track1.album = album
        assert track1.album == album

    def test_attributes_fail(self):
        track1 = Track(1, 'Shivers')
        track2 = Track(2, 'Heat Waves')

        # Test trying to assign wrong types to track_url
        track1.track_url = 23

        # Assigning wrong types should set track_url = None
        assert track1.track_url is None

        # Test invalid type for title setter sets title to None
        track1.title = 1256
        assert track1.title is None

        track1.title = ''
        assert track1.title is None

        with pytest.raises(ValueError):
            track1.track_duration = '300 seconds'

        with pytest.raises(ValueError):
            track2.track_duration = -20

        assert track1.track_duration is None
        assert track2.track_duration is None

        # Assigning artist of invalid type does not make change
        track1.artist = 3235
        track2.artist = 'invalid artist'
        assert track1.artist is None
        assert track2.artist is None

        # Assigning invalid types sets the attribute to None
        track1.album = 1983
        track2.album = 'Invalid album'
        assert track1.album is None
        assert track2.album is None

    def test_genre_methods(self):
        track1 = Track(1, 'Shivers')
        genre1 = Genre(10, 'Jazz')
        genre2 = Genre(11, 'Clasical')

        track1.add_genre(genre1)
        track1.add_genre(genre2)
        assert track1.genres == [genre1, genre2]

        # Should do nothing
        track1.add_genre('32')
        assert track1.genres == [genre1, genre2]

    def test_equality(self):
        track1 = Track(1, 'Shivers')
        track2 = Track(2, 'Heat Waves')
        track3 = Track(3, 'Bad Habit')

        assert track1 == track1
        assert track2 == track2
        assert track1 != track2
        assert track1 != track3

        assert track2 != 30
        assert track3 != 'Bad Habit'

    def test_sorting(self):
        track1 = Track(1, 'Shivers')
        track2 = Track(8, 'Heat Waves')
        track3 = Track(10, 'Bad Habit')

        assert track1 < track2
        assert track2 < track3
        assert track3 > track1

        track_list = [track3, track1, track2, track1]
        assert sorted(track_list) == [track1, track1, track2, track3]

    def test_set(self):
        track1 = Track(1, 'Shivers')
        track2 = Track(8, 'Heat Waves')
        track3 = Track(10, 'Bad Habit')

        track_set = set()
        track_set.add(track1)
        track_set.add(track2)
        track_set.add(track3)

        assert len(track_set) == 3

        track_set.discard(track1)
        assert sorted(track_set) == [track2, track3]

        track_set.discard(track2)
        track_set.discard(track3)
        assert len(track_set) == 0


class TestReview:

    def test_construction(self):
        track1 = Track(2, 'Heat Waves')
        user = User("useruser", "passwordpasword")
        review1 = Review(user, track1, 'Sample review', 3)
        review2 = Review(user, track1, ' Another review ', 2)

        assert review1.track == track1
        assert review1.review_text == 'Sample review'
        assert review1.rating == 3
        assert review2.review_text == 'Another review'

        review2 = Review(user, 'Invalid track', 23, 1)
        assert review2.track is None
        assert review2.review_text == 'N/A'

        with pytest.raises(ValueError):
            Review(user, track1, 'Text', 'rating')

        # Negative value of comment raises error
        with pytest.raises(ValueError):
            Review(user, track1, 'Text', -5)
        # Rating value > 5 raises error
        with pytest.raises(ValueError):
            Review(user, track1, 'Text', 10)

    def test_attributes(self):
        user = User("useruser", "passwordpasword")
        track1 = Track(2, 'Heat Waves')
        review1 = Review(user, track1, 'Sample review', 3)

        assert review1.track == track1

        # Test review_text getter & setter
        review1.review_text = '  Fixed review '
        assert review1.review_text == 'Fixed review'

        # Test rating getter & setter
        review1.rating = 5
        assert review1.rating == 5

    def test_attributes_fail(self):
        user = User("useruser", "passwordpasword")
        track1 = Track(2, 'Heat Waves')
        review1 = Review(user, track1, 'Sweater Weather', 2)

        review1.review_text = 5
        assert review1.review_text is None

        with pytest.raises(ValueError):
            review1.rating = '5'

        with pytest.raises(ValueError):
            review1.rating = -1

        with pytest.raises(ValueError):
            review1.rating = 10

    def test_equality(self):
        user = User("useruser", "passwordpasword")
        track1 = Track(2, 'Heat Waves')
        review1 = Review(user, track1, 'Sweater Weather', 2)
        review3 = Review(user, track1, 'Sweater Weather', 5)
        review4 = Review(user, track1, 'Sweater Weather 2', 2)
        review5 = Review(user, None, 'Sweater Weather', 2)

        assert review1 == review1
        assert review1 != review3
        assert review1 != review4
        assert review1 != review5

        assert review1 != 'Sweater Weather'
        assert review1 != 2


class TestUser:

    def test_construction(self):
        user1 = User('amotys', 'amotys277')
        user2 = User('  yunwi5  ', 'urrabbit978')

        assert str(user1) == '<User amotys, user password = amotys277>'
        assert str(user2) == '<User yunwi5, user password = urrabbit978>'

        # Test user_name is all lowercase
        user3 = User(' GAVI ', 'gavi1928')
        assert user3.user_name == 'gavi'

        # Invalid user_name type sets user_name to None
        user4 = User(1259, 'memphis212')
        assert user4.user_name is None

        # Invalid password type set password to None
        user5 = User('Memphis', 325)
        assert user5.password is None

        user5 = User('Memphis', '')
        assert user5.password is None

        # Password length < 7 sets password to None
        user5 = User('memphis', 'mempi')
        assert user5.password is None

        # Password of length 7 sets the password correctly
        user6 = User('Memphis', 'mempi12')
        assert user6.password == 'mempi12'

    # User class has getters for each attribute, but no setters.
    def test_attributes(self):
        user1 = User('  AMOTYS  ', 'amotys277')
        assert user1.user_name == 'amotys'
        assert user1.password == 'amotys277'

    def test_attributes_fail(self):
        user1 = User('  LEOROSE  ', 'LEOROSE277')

        with pytest.raises(AttributeError):
            user1.user_name = 'changed'

        with pytest.raises(AttributeError):
            user1.password = 'asdfe'

    def test_equality(self):
        user1 = User('amotys', 'amotys277')
        user1_copy = User('amotys', 'amotys277')
        user2 = User('gavi', 'gavi9281')
        user3 = User('phil', 'phi8901')

        assert user1 == user1_copy
        assert user1 != user2
        assert user2 != user3

        # Check equality with different types
        track1 = Track(9998, 'Chill with me')
        assert user1 != track1
        assert user1 != 'some user'
        assert user2 != 7120
        assert user3 is not None

    def test_track_methods(self):
        """ Test add_liked_track() and remove_liked_track() methods """
        user1 = User('pedri', 'pedri9281')
        track1 = Track(1, 'Shivers')
        track2 = Track(2, 'Heat Waves')
        track3 = Track(3, 'Bad Habit')

        user1.add_liked_track(track1)
        user1.add_liked_track(track2)
        user1.add_liked_track(track3)
        assert user1.liked_tracks == [track1, track2, track3]

        track1_copy = Track(1, 'Shivers')
        user1.add_liked_track(track1_copy)
        assert len(user1.liked_tracks) == 3

    def test_review_methods(self):
        """ Test add_review() and remove_review() methods """
        user1 = User('gavi', 'gavi9281')
        track1 = Track(2, 'Heat Waves')
        review1 = Review(user1, track1, 'review 1', 2)
        review2 = Review(user1, track1, 'review 2', 3)
        review3 = Review(user1, track1, 'review 3', 5)

        assert user1.reviews == []

        user1.add_review(review1)
        user1.add_review(review2)
        user1.add_review(review3)
        assert user1.reviews == [review1, review2, review3]

        # Test it does not add the same review twice
        user1.add_review(review1)
        assert len(user1.reviews) == 3

        # Test it does not add review of invalid types
        user1.add_review(300)
        user1.add_review('review')
        user1.add_review(None)
        assert len(user1.reviews) == 3

        user1.remove_review(review2)
        user1.remove_review(review1)
        assert user1.reviews == [review3]

        # Test removing non-existing review does nothing
        user1.remove_review(review2)
        assert user1.reviews == [review3]

        user1.remove_review(None)
        user1.remove_review(928)
        user1.remove_review('review')
        assert user1.reviews == [review3]