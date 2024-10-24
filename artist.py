from base import db


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(250))
    facebook_link = db.Column(db.String(250))
    website_link = db.Column(db.String(250))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship("Show", backref="artist", lazy=True)

    def _repr__(self):
        return f"<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.image_link} {self.facebook_link} {self.website_link} {self.seeking_venue} {self.seeking_description}>"

    def __get__(self):

        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "genres": self.genres,
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "website_link": self.website_link,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description,
        }
