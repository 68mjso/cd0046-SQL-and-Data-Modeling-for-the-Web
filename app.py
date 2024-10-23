# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from base import app, db
from artist import Artist
from venue import Venue
from show import Show
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


# TODO: connect to a local postgresql database

migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = Venue.query.all()
    groups = {}

    for venue in data:
        key = (venue.city, venue.state)
        if key not in groups:
            groups[key] = []
        groups[key].append(
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(
                    [show for show in venue.shows if show.start_time > datetime.now()]
                ),
            }
        )
    data = []
    for (city, state), venues in groups.items():
        data.append({"city": city, "state": state, "venues": venues})
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term", "")
    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    response = {
        "count": len(venues),
        "data": [
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(
                    [show for show in venue.shows if show.start_time > datetime.now()]
                ),
            }
            for venue in venues
        ],
    }
    return render_template(
        "pages/search_venues.html", results=response, search_term=search_term
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    current_time = datetime.now()
    result: Venue = Venue.query.get(venue_id)
    venue = result.__get__()
    past_shows_query = (
        db.session.query(
            Show.start_time,
            Artist.id.label("artist_id"),
            Artist.name.label("artist_name"),
            Artist.image_link.label("artist_image_link"),
        )
        .join(Artist, Show.artist_id == Artist.id)
        .filter(Show.venue_id == venue_id, Show.start_time < current_time)
        .all()
    )

    upcoming_shows_query = (
        db.session.query(
            Show.start_time,
            Artist.id.label("artist_id"),
            Artist.name.label("artist_name"),
            Artist.image_link.label("artist_image_link"),
        )
        .join(Artist, Show.artist_id == Artist.id)
        .filter(Show.venue_id == venue_id, Show.start_time >= current_time)
        .all()
    )

    past_shows = [
        {
            "artist_id": show.artist_id,
            "artist_name": show.artist_name,
            "artist_image_link": show.artist_image_link,
            "start_time": show.start_time.isoformat(),
        }
        for show in past_shows_query
    ]

    upcoming_shows = [
        {
            "artist_id": show.artist_id,
            "artist_name": show.artist_name,
            "artist_image_link": show.artist_image_link,
            "start_time": show.start_time.isoformat(),
        }
        for show in upcoming_shows_query
    ]

    upcoming_shows_count = len(upcoming_shows)
    past_shows_count = len(past_shows)
    venue["upcoming_shows_count"] = upcoming_shows_count
    venue["past_shows_count"] = past_shows_count
    venue["past_shows"] = past_shows
    venue["upcoming_shows"] = upcoming_shows
    return render_template("pages/show_venue.html", venue=venue)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    try:
        # TODO: insert form data as a new Venue record in the db, instead
        # TODO: modify data to be the data object returned from db insertion
        new_venue = Venue(
            name=request.form["name"],
            city=request.form["city"],
            state=request.form["state"],
            address=request.form["address"],
            phone=request.form["phone"],
            genres=",".join(request.form.getlist("genres")),
            facebook_link=request.form["facebook_link"],
            image_link=request.form["image_link"],
            website_link=request.form["website_link"],
            seeking_talent=request.form.get("seeking_talent", "n") == "y",
            seeking_description=request.form["seeking_description"],
        )
        db.session.add(new_venue)
        db.session.commit()
        # on successful db insert, flash success
        flash("Venue " + request.form["name"] + " was successfully listed!")
    except Exception as e:
        # TODO: on unsuccessful db insert, flash an error instead.
        db.session.rollback()
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be listed."
        )
        print(e)
    finally:
        db.session.close()

    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash(f'Venue {venue["name"]} was successfully deleted!')
    except:
        db.session.rollback()
        flash(f"An error occurred. Venue could not be deleted.")
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database
    result = Artist.query.all()
    data = []
    for artist in result:
        artist_data = {"id": artist.id, "name": artist.name}
        data.append(artist_data)
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get("search_term", "")
    artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    response = {
        "count": len(artists),
        "data": [
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": len(
                    [show for show in artist.shows if show.start_time > datetime.now()]
                ),
            }
            for artist in artists
        ],
    }
    # response={
    #   "count": 1,
    #   "data": [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "num_upcoming_shows": 0,
    #   }]
    # }
    return render_template(
        "pages/search_artists.html", results=response, search_term=search_term
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    current_time = datetime.now()
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    result: Artist = Artist.query.get(artist_id)
    artist = result.__get__()

    past_shows_query = (
        db.session.query(
            Show.start_time,
            Venue.id.label("venue_id"),
            Venue.name.label("venue_name"),
            Venue.image_link.label("venue_image_link"),
        )
        .join(Venue, Show.venue_id == Venue.id)
        .filter(Show.artist_id == artist_id, Show.start_time < current_time)
        .all()
    )

    upcoming_shows_query = (
        db.session.query(
            Show.start_time,
            Venue.id.label("venue_id"),
            Venue.name.label("venue_name"),
            Venue.image_link.label("venue_image_link"),
        )
        .join(Venue, Show.venue_id == Venue.id)
        .filter(Show.artist_id == artist_id, Show.start_time >= current_time)
        .all()
    )

    past_shows = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venue_name,
            "venue_image_link": show.venue_image_link,
            "start_time": show.start_time.isoformat(),
        }
        for show in past_shows_query
    ]

    upcoming_shows = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venue_name,
            "venue_image_link": show.venue_image_link,
            "start_time": show.start_time.isoformat(),
        }
        for show in upcoming_shows_query
    ]

    upcoming_shows_count = len(upcoming_shows)
    past_shows_count = len(past_shows)
    artist["upcoming_shows_count"] = upcoming_shows_count
    artist["past_shows_count"] = past_shows_count
    artist["past_shows"] = past_shows
    artist["upcoming_shows"] = upcoming_shows

    return render_template("pages/show_artist.html", artist=artist)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    result: Artist = Artist.query.get(artist_id)
    artist = result.__get__()
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist: Artist = Artist.query.get(artist_id)
    artist.name = request.form["name"] or ""
    artist.city = request.form["city"] or ""
    artist.state = request.form["state"] or ""
    artist.phone = request.form["phone"] or ""
    artist.genres = ",".join(request.form.getlist("genres")) or ""
    artist.facebook_link = request.form["facebook_link"] or ""
    artist.image_link = request.form["image_link"] or ""
    artist.website_link = request.form["website_link"] or ""
    artist.seeking_venue = request.form.get("seeking_venue", "n") == "y"
    artist.seeking_description = request.form["seeking_description"] or ""
    db.session.commit()
    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    result: Venue = Venue.query.get(venue_id)
    venue = result.__get__()
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue: Venue = Venue.query.get(venue_id)
    venue.name = request.form["name"]
    venue.city = request.form["city"]
    venue.state = request.form["state"]
    venue.address = request.form["address"]
    venue.phone = request.form["phone"]
    venue.genres = ",".join(request.form.getlist("genres"))
    venue.facebook_link = request.form["facebook_link"]
    venue.image_link = request.form["image_link"]
    venue.website_link = request.form["website_link"]
    venue.seeking_talent = request.form.get("seeking_talent", "n") == "y"
    venue.seeking_description = request.form["seeking_description"]
    db.session.commit()
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    try:
        # TODO: insert form data as a new Artist record in the db, instead
        # TODO: modify data to be the data object returned from db insertion
        new_artist = Artist(
            name=request.form["name"] or "",
            city=request.form["city"] or "",
            state=request.form["state"] or "",
            phone=request.form["phone"] or "",
            genres=",".join(request.form.getlist("genres")) or "",
            facebook_link=request.form["facebook_link"] or "",
            image_link=request.form["image_link"] or "",
            website_link=request.form["website_link"] or "",
            seeking_venue=request.form.get("seeking_venue", "n") == "y",
            seeking_description=request.form["seeking_description"] or "",
        )
        db.session.add(new_artist)
        db.session.commit()
        # on successful db insert, flash success
        flash("Artist " + request.form["name"] + " was successfully listed!")
    except Exception as e:
        # TODO: on unsuccessful db insert, flash an error instead.
        db.session.rollback()
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be listed."
        )
        print(e)
    finally:
        db.session.close()
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    result = Show.query.all()
    data = []
    for show in result:
        data.append(show.__get__())
    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    try:
        artist_id = request.form["artist_id"]
        venue_id = request.form["venue_id"]
        start_time = request.form["start_time"]
        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash("Show was successfully listed!")
    except Exception as e:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash("An error occurred. Show could not be listed.")
    finally:
        db.session.close()
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
