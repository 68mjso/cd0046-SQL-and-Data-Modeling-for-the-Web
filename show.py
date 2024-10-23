from base import db

from artist import Artist
from venue import Venue


class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)

    def _repr__(self):
        return f"<Show {self.venue_id} {self.artist_id} {self.start_time}>"

    def __get__(self):
        venue = Venue.query.get(self.venue_id)
        artist = Artist.query.get(self.artist_id)
        return {
            "id": self.id,
            "venue_id": self.venue_id,
            "venue_name": venue.name,
            "artist_id": self.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": self.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        }
