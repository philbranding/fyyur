# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.sql import crud

from forms import *
from flask_migrate import Migrate

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


""" 
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"], ###
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com", ###
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True, ###
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.", ###
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  """


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


""" 
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",###
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True, ###
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!", ###
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  """


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    upcoming = db.Column(db.Boolean, nullable=False, default=True)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # data = Venue.query.all()
    # return render_template('pages/venues.html', areas=data);
    distinct_grouping = Venue.query.distinct(Venue.city, Venue.state).all()
    for venue in distinct_grouping:
        return render_template('pages/venues.html', areas=distinct_grouping)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    term = request.form.get('search_term', '')
    found = Venue.query.filter(Venue.name.ilike(f'%{term}%')).all()
    response = {
        'count': len(found),
        'data': [{
            'id': v_term.id,
            'name': v_term.name,
            'num_upcoming_shows': len(v_term.upcoming_shows)
        } for v_term in found]
    }
    return render_template('pages/search_venues.html', results=response, search_term=term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # data = Venue.query.get_or_404(venue_id)
    # return render_template('pages/show_venue.html', venue=data)
    venues = Show.query.all()
    venue = Venue.query.get_or_404(venue_id)

    for venue in venues:
        data = {
            'artist_id': shows.artist_id,
            'artist_name': shows.artist.name,
            'artist_image_link': shows.artist.image_link
        }
        return render_template('pages/show_venue.html', venue=data)

    return render_template('pages/home.html')


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    venue_form = VenueForm(request.form)

    new_venue = Venue(

        name=venue_form.name.data,
        genres=','.join(venue_form.genres.data),
        address=venue_form.address.data,
        city=venue_form.city.data,
        state=venue_form.state.data,
        phone=venue_form.phone.data,
        facebook_link=venue_form.facebook_link.data,
        image_link=venue_form.image_link.data)

    # on successful db insert, flash success
    db.session.add(new_venue)
    db.session.commit()
    venue = db.session.query(Venue).filter(Venue.id == new_venue.id)
    if not venue:
        flash('failed to save in the database')
        return redirect('/venues')
    else:
        flash('new entry was successful')
    return redirect('/venues')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    deleted_venue = Venue.query.filter_by(venue_id).first_or_404()
    if deleted_venue is None:
        return {"error": "not found"}
        db.session.delete(deleted_venue)
        db.session.commit()
    return {"message": "Venue Deleted"}
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artist = Artist.query.order_by(Artist.id.name).all()
    return render_template('pages/artists.html', artists=artist)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    term = request.form.get('search_term', '')
    found = Artist.query.filter(Artist.name.ilike(f'%{term}%')).all()
    response = {
        'count': len(found),
        'data': [{
            'id': s_term.id,
            'name': s_term.name,
        } for s_term in found]
    }

    return render_template('pages/search_artists.html', results=response,search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = db.session.query(Artist).filter_by(id=artist_id).first()
    if not artist:
        flash('User not found!', 'error')
        return redirect('/artists')
    result = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(';'),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "seeking_venue": artist.seeking_talent,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "facebook_link": artist.facebook_link,
        "website": artist.website,
    }

    return render_template('pages/show_artist.html', artist=result)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    e_artist = Artist.query.get(artist_id)
    artist = None if e_artist is None else {
            'id': e_artist.id,
            'name': e_artist.name,
            'genres': json.dumps(e_artist.genres),
            'city': e_artist.city,
            'state': e_artist.state,
            'phone': e_artist.phone,
            'website_link': e_artist.website,
            'facebook_link': e_artist.facebook_link,
            'seeking_talent': e_artist.seeking_talent,
            'seeking_description': e_artist.seeking_description,
            'image_link': e_artist.image_link,
        }
    form = ArtistForm(data=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    if artist is None:
        flash(f'No such artist (id: {artist_id})')
        return redirect(url_for("artists"))
        form.facebook_link.validators = []
        form.populate_obj(artist)
        selected = request.form.getlist('genres')
        artist.website = request.form['website_link']
        flash(f'Updated info for artist {artist.name}')
        flash('Unable to update artist due to invalid data', 'error')
    return render_template('forms/edit_artist.html', form=form, artist=artist)
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # TODO: populate form with values from venue with ID <venue_id>
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
    venue = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(';') if venue.genres else [],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }
    return render_template('forms/edit_venue.html', form=form, venue=venue)

    """
  INSERT INTO public."Venue"(id ,name ,genres,address ,city ,state ,phone ,website , facebook_link, seeking_talent, seeking_description, image_link)
  VALUES (1, 'The Musical Hop',('Jazz', 'Reggae', 'Swing', 'Classical', 'Folk'), '1015 Folsom Street', 'San Francisco', 'CA', '123-123-1234','https://www.themusicalhop.com', 'https://www.facebook.com/TheMusicalHop', 'True', 'We are on the lookout for a local artist to play every two weeks. Please call us.', 'https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60');
  """
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    form_data = request.form
    artist = Artist()
    artist.name = form_data['name']
    artist.city = form_data['city']
    artist.state = form_data['state']
    artist.phone = form_data['phone']
    artist.genres = ';'.join(form_data.getlist('genres'))
    artist.image_link = form_data.get('image_link', '')
    artist.facebook_link = form_data.get('facebook_link', '')
    artist.website = form_data.get('website', '')
    artist.seeking_venue = True if form_data['seeking_venue'] == 'true' else False
    artist.seeking_description = form_data.get('seeking_description', '')
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    show = Show.query.all()
    data = []
    for show in show:
        data.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time)
            })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)

    show = Show(
        venue_id=form.venue_id.data,
        artist_id=form.artist_id.data,
        start_time=form.start_time.data
    )

    try:
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully placed')
    except:
        flash('Sorry, an error occurred. Show could not be listed')
    finally:
        db.session.close()

    # on successful db insert, flash success
    # flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
