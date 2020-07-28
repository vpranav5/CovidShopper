import googlemaps
import json
import time
import usaddress
import requests
import sys
import os
from flask import Flask, session, render_template, request, url_for, session, redirect, jsonify,  send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import text
from models import City, Hospital, Drugstore, db, app
from request import cities_list
import tests
from flask_cors import CORS

# app = Flask(__name__)

CORS(app)

baseURL = "https://covidfighter-280919.nn.r.appspot.com/api"


def getDrugstoresInsideByQuery(name = '', city = ''):
    drugstores_dict = {'drugstores': list()}

    if name is None:
        name = ''
    if city is None:
        city = ''

    name = name.lower()
    city = city.lower()

    name_search = "%{}%".format(name)
    city_search = "%{}%".format(city)

    try:
        if name == "" and city == "":
            drugstores_list = list()
            with open('all_drugstores.txt') as json_file:
                drugstores_list = json.load(json_file)
            return jsonify(drugstores_list), 200

        elif name == "":
            city_result = db.session.query(City).filter(City.name.ilike(city_search)).all()

            if len(city_result) == 0:
                return jsonify([]), 200

            for city in city_result:
                drugstore_results = db.session.query(Drugstore).filter_by(city_id=city.id).all()

                if len(drugstore_results) == 0:
                    return jsonify([]), 200

                for drugstore in drugstore_results:
                    drugstore_dict = {'name': drugstore.name, 'address': drugstore.address, 'latitude': drugstore.latitude,
                                      'longitude': drugstore.longitude, 'opening_hours': drugstore.opening_hours, 'business_status': drugstore.business_status,
                                      'google_maps_url': drugstore.google_maps_url}

                    drugstores_dict['drugstores'].append(drugstore_dict)

        elif city == "":
            drugstore_results = db.session.query(Drugstore).filter(Drugstore.name.ilike(name_search)).all()

            if len(drugstore_results) == 0:
                return jsonify([]), 200

            for drugstore in drugstore_results:
                drugstore_dict = {'name': drugstore.name, 'address': drugstore.address, 'latitude': drugstore.latitude,
                                      'longitude': drugstore.longitude, 'opening_hours': drugstore.opening_hours, 'business_status': drugstore.business_status,
                                      'google_maps_url': drugstore.google_maps_url}

                drugstores_dict['drugstores'].append(drugstore_dict)

        else:
            drugstore_results = db.session.query(Drugstore).join(City).filter(Drugstore.name.ilike(name_search)).filter(City.name.ilike(city_search)).all()

            if len(drugstore_results) == 0:
                return jsonify([]), 200

            for drugstore in drugstore_results:
                drugstore_dict = {'name': drugstore.name, 'address': drugstore.address, 'latitude': drugstore.latitude,
                                  'longitude': drugstore.longitude, 'opening_hours': drugstore.opening_hours, 'business_status': drugstore.business_status,
                                  'google_maps_url': drugstore.google_maps_url}

                drugstores_dict['drugstores'].append(drugstore_dict)

        return jsonify(drugstores_dict['drugstores']), 200
    except Exception:
        return jsonify(error_dict), 500


def getHospitalsInsideByQuery(name = '', city = ''):
    hospitals_dict = {'hospitals': list()}

    if name is None:
        name = ''
    if city is None:
        city = ''

    name = name.lower()
    city = city.lower()

    name_search = "%{}%".format(name)
    city_search = "%{}%".format(city)

    try:
        if name == "" and city == "":
            return jsonify([]), 200

        elif name == "":
            city_result = db.session.query(City).filter(City.name.ilike(city_search)).all()

            if len(city_result) == 0:
                return jsonify([]), 200

            for city in city_result:
                hospital_results = db.session.query(Hospital).filter_by(city_id=city.id).all()

                if len(hospital_results) == 0:
                    return jsonify([]), 200

                for hospital in hospital_results:
                    hospital_dict = {'name': hospital.name, 'address': hospital.address, 'latitude': hospital.latitude,
                                     'longitude': hospital.longitude, 'opening_hours': hospital.opening_hours, 'business_status': hospital.business_status,
                                     'google_maps_url': hospital.google_maps_url}

                    hospitals_dict['hospitals'].append(hospital_dict)

        elif city == "":
            hospital_results = db.session.query(Hospital).filter(Hospital.name.ilike(name_search)).all()

            if len(hospital_results) == 0:
                return jsonify([]), 200

            for hospital in hospital_results:
                hospital_dict = {'name': hospital.name, 'address': hospital.address, 'latitude': hospital.latitude,
                                 'longitude': hospital.longitude, 'opening_hours': hospital.opening_hours, 'business_status': hospital.business_status,
                                 'google_maps_url': hospital.google_maps_url}

                hospitals_dict['hospitals'].append(hospital_dict)

        else:
            hospital_results = db.session.query(Hospital).join(City).filter(Hospital.name.ilike(name_search)).filter(City.name.ilike(city_search)).all()

            if len(hospital_results) == 0:
                return jsonify([]), 200

            for hospital in hospital_results:
                drugstore_dict = {'name': hospital.name, 'address': hospital.address, 'latitude': hospital.latitude,
                                  'longitude': hospital.longitude, 'opening_hours': hospital.opening_hours, 'business_status': hospital.business_status,
                                  'google_maps_url': hospital.google_maps_url}

                hospital_results['hospitals'].append(drugstore_dict)

        return jsonify(hospitals_dict['hospitals']), 200
    except Exception:
        return jsonify(error_dict), 500


def getCitiesInsideByQuery(name=''):
    cities_dict = {'cities': list()}

    if name is None:
        name = ''

    name = name.lower()
    name_search = "%{}%".format(name)

    try:
        if name == '':
            return jsonify([]), 200
        else:
            city_result = db.session.query(City).filter(City.name.ilike(name_search)).all()

            if len(city_result) == 0:
                return jsonify([]), 200

            for city in city_result:
                city_dict = {"name": city.name, "state": city.state,
                             "latitude": city.latitude, "longitude": city.longitude,
                             "population": city.population}

                cities_dict['cities'].append(city_dict)

        return cities_dict['cities']
    except Exception:
        return jsonify([]), 200


# # API ENDPOINTS FROM HERE ON DOWN #


error_dict = {
            'code': 500,
            'message': 'An error occurred'
        }

@app.route('/test', methods=['GET', 'POST'])
def test():
    """
        about page, contains introductions of each team memeber, data source used, and all the required
    """
    os.system('coverage run --branch tests.py >  tests.out 2>&1')
    output = open('tests.out', 'r')
    results = output.readlines()
    return jsonify(results), 200


@app.route("/api/City/", methods = ['GET', 'POST'])
def getCitiesByQuery():
    name = request.args.get("name")
    print('Name: ')
    print(name)
    cities_dict = {'cities': list()}
    try:
        if name is None:
            return jsonify({}), 200
        else:
            city_result = db.session.query(City).filter_by(name=name).all()

            if len(city_result) == 0:
                return jsonify({}), 200

            for city in city_result:
                city_dict = {"id": city.id, "name": city.name, "state": city.state,
                             "latitude": city.latitude, "longitude": city.longitude,
                             "population": city.population,
                             "hospitals": [hospital.id for hospital in city.hospitals],
                             "drugstores": [drugstore.id for drugstore in city.drugstores]}

                cities_dict['cities'].append(city_dict)

        return jsonify(cities_dict), 200
    except Exception:
        return jsonify(error_dict), 500


@app.route("/api/City/<int:city_id>")
def getCityById(city_id: int):
    try:
        city_result = db.session.query(City).filter_by(id=city_id).all()

        if len(city_result) == 0:
            return jsonify({}), 200

        city = city_result[0]

        city_dict = {"id": city.id, "name": city.name, "state": city.state,
                     "latitude": city.latitude, "longitude": city.longitude,
                     "population": city.population,
                     "hospitals": [hospital.id for hospital in city.hospitals],
                     "drugstores": [drugstore.id for drugstore in city.drugstores]}

        return jsonify(city_dict), 200
    except Exception:
        return jsonify(error_dict), 500


@app.route("/api/Hospital/")
def getHospitalsByQuery():
    name = request.args.get("name")
    city = request.args.get("city")

    hospitals_dict = {'hospitals': list()}
    try:
        if name is None and city is None:
            return jsonify({}), 200

        elif name is None:
            city_result = db.session.query(City).filter_by(name=city).all()

            if len(city_result) == 0:
                return jsonify({}), 200

            for city in city_result:
                hospital_results = db.session.query(Hospital).filter_by(city_id=city.id).all()

                if len(hospital_results) == 0:
                    continue

                for hospital in hospital_results:
                    hospital_dict = {'id': hospital.id, 'name': hospital.name, 'address': hospital.address, 'zipcode': hospital.zipcode, 'latitude': hospital.latitude,
                                     'longitude': hospital.longitude, 'opening_hours': hospital.opening_hours, 'business_status': hospital.business_status,
                                     'google_maps_url': hospital.google_maps_url, 'city_id': hospital.city_id,
                                     'drugstores_nearby': [drugstore.id for drugstore in hospital.drugstores_nearby]}

                    hospitals_dict['hospitals'].append(hospital_dict)

        elif city is None:
            hospital_results = db.session.query(Hospital).filter_by(name=name).all()

            if len(hospital_results) == 0:
                return jsonify({}), 200

            for hospital in hospital_results:
                hospital_dict = {'id': hospital.id, 'name': hospital.name, 'address': hospital.address, 'zipcode': hospital.zipcode, 'latitude': hospital.latitude,
                                 'longitude': hospital.longitude, 'opening_hours': hospital.opening_hours, 'business_status': hospital.business_status,
                                 'google_maps_url': hospital.google_maps_url, 'city_id': hospital.city_id,
                                 'drugstores_nearby': [drugstore.id for drugstore in hospital.drugstores_nearby]}

                hospitals_dict['hospitals'].append(hospital_dict)

        else:
            city_result = db.session.query(City).filter_by(name=city).all()

            if len(city_result) == 0:
                return jsonify({}), 200

            for city in city_result:
                hospital_results = db.session.query(Hospital).filter_by(city_id=city.id, name=name).all()

                if len(hospital_results) == 0:
                    continue

                for hospital in hospital_results:
                    hospital_dict = {'id': hospital.id, 'name': hospital.name, 'address': hospital.address, 'zipcode': hospital.zipcode, 'latitude': hospital.latitude,
                                     'longitude': hospital.longitude, 'opening_hours': hospital.opening_hours, 'business_status': hospital.business_status,
                                     'google_maps_url': hospital.google_maps_url, 'city_id': hospital.city_id,
                                     'drugstores_nearby': [drugstore.id for drugstore in hospital.drugstores_nearby]}

                    hospitals_dict['hospitals'].append(hospital_dict)

        return jsonify(hospitals_dict), 200
    except Exception:
        return jsonify(error_dict), 500


@app.route("/api/Hospital/nearby/<string:drugstore_id>")
def getNearbyHospitals(drugstore_id: str):
    hospitals_dict = {'hospitals': list()}
    try:
        drugstore_result = db.session.query(Drugstore).filter_by(id=drugstore_id).all()

        if len(drugstore_result) == 0:
            return jsonify({}), 200

        drugstore = drugstore_result[0]

        for hospital in drugstore.hospitals_nearby:
            hospital_dict = {'id': hospital.id, 'name': hospital.name, 'address': hospital.address, 'zipcode': hospital.zipcode, 'latitude': hospital.latitude,
                             'longitude': hospital.longitude, 'opening_hours': hospital.opening_hours, 'business_status': hospital.business_status,
                             'google_maps_url': hospital.google_maps_url, 'city_id': hospital.city_id,
                             'drugstores_nearby': [drugstore.id for drugstore in hospital.drugstores_nearby]}

            hospitals_dict['hospitals'].append(hospital_dict)

        return jsonify(hospitals_dict), 200
    except Exception:
        return jsonify(error_dict), 500


@app.route("/api/Hospital/<string:hospital_id>")
def getHospitalById(hospital_id: str):
    try:
        hospital_result = db.session.query(Hospital).filter_by(id=hospital_id).all()

        if len(hospital_result) == 0:
            return jsonify({}), 200

        hospital = hospital_result[0]

        hospital_dict = {'id': hospital.id, 'name': hospital.name, 'address': hospital.address, 'zipcode': hospital.zipcode, 'latitude': hospital.latitude,
                         'longitude': hospital.longitude, 'opening_hours': hospital.opening_hours, 'business_status': hospital.business_status,
                         'google_maps_url': hospital.google_maps_url, 'city_id': hospital.city_id,
                         'drugstores_nearby': [drugstore.id for drugstore in hospital.drugstores_nearby]}

        return jsonify(hospital_dict), 200
    except Exception:
        return jsonify(error_dict), 500


@app.route("/api/Drugstore/")
def getDrugstoresByQuery():
    city = request.args.get("city")

    drugstores_dict = {'drugstores': list()}
    try:
        if name is None and city is None:
            return jsonify({}), 200

        elif name is None:
            city_result = db.session.query(City).filter_by(name=city).all()

            if len(city_result) == 0:
                return jsonify({}), 200

            for city in city_result:
                drugstore_results = db.session.query(Drugstore).filter_by(city_id=city.id).all()

                if len(drugstore_results) == 0:
                    continue

                for drugstore in drugstore_results:
                    drugstore_dict = {'id': drugstore.id, 'name': drugstore.name, 'address': drugstore.address, 'zipcode': drugstore.zipcode, 'latitude': drugstore.latitude,
                                      'longitude': drugstore.longitude, 'opening_hours': drugstore.opening_hours, 'business_status': drugstore.business_status,
                                      'google_maps_url': drugstore.google_maps_url, 'city_id': drugstore.city_id,
                                      'hospitals_nearby': [hospital.id for hospital in drugstore.hospitals_nearby]}

                    drugstores_dict['drugstores'].append(drugstore_dict)

        elif city is None:
            drugstore_results = db.session.query(Drugstore).filter_by(name=name).all()

            if len(drugstore_results) == 0:
                return jsonify({}), 200

            for drugstore in drugstore_results:
                drugstore_dict = {'id': drugstore.id, 'name': drugstore.name, 'address': drugstore.address, 'zipcode': drugstore.zipcode, 'latitude': drugstore.latitude,
                                  'longitude': drugstore.longitude, 'opening_hours': drugstore.opening_hours, 'business_status': drugstore.business_status,
                                  'google_maps_url': drugstore.google_maps_url, 'city_id': drugstore.city_id,
                                  'hospitals_nearby': [hospital.id for hospital in drugstore.hospitals_nearby]}

                drugstores_dict['drugstores'].append(drugstore_dict)

        else:
            city_result = db.session.query(City).filter_by(name=city).all()

            if len(city_result) == 0:
                return jsonify({}), 200

            for city in city_result:
                drugstore_results = db.session.query(Drugstore).filter_by(city_id=city.id, name=name).all()

                if len(drugstore_results) == 0:
                    continue

                for drugstore in drugstore_results:
                    drugstore_dict = {'id': drugstore.id, 'name': drugstore.name, 'address': drugstore.address, 'zipcode': drugstore.zipcode, 'latitude': drugstore.latitude,
                                      'longitude': drugstore.longitude, 'opening_hours': drugstore.opening_hours, 'business_status': drugstore.business_status,
                                      'google_maps_url': drugstore.google_maps_url, 'city_id': drugstore.city_id,
                                      'hospitals_nearby': [hospital.id for hospital in drugstore.hospitals_nearby]}

                    drugstores_dict['drugstores'].append(drugstore_dict)

        return jsonify(drugstores_dict), 200
    except Exception:
        return jsonify(error_dict), 500


@app.route("/api/Drugstore/nearby/<string:hospital_id>")
def getNearbyDrugstores(hospital_id: str):
    drugstores_dict = {'drugstores': list()}
    try:
        hospital_result = db.session.query(Hospital).filter_by(id=hospital_id).all()

        if len(hospital_result) == 0:
            return jsonify({}), 200

        hospital = hospital_result[0]

        for drugstore in hospital.drugstores_nearby:
            drugstore_dict = {'id': drugstore.id, 'name': drugstore.name, 'address': drugstore.address, 'zipcode': drugstore.zipcode, 'latitude': drugstore.latitude,
                              'longitude': drugstore.longitude, 'opening_hours': drugstore.opening_hours, 'business_status': drugstore.business_status,
                              'google_maps_url': drugstore.google_maps_url, 'city_id': drugstore.city_id,
                              'hospitals_nearby': [hospital.id for hospital in drugstore.hospitals_nearby]}

            drugstores_dict['drugstores'].append(drugstore_dict)

        return jsonify(drugstores_dict), 200
    except Exception:
        return jsonify(error_dict), 500


@app.route("/api/Drugstore/<string:drugstore_id>")
def getDrugstoreById(drugstore_id: str):
    try:
        drugstore_result = db.session.query(Drugstore).filter_by(id=drugstore_id).all()

        if len(drugstore_result) == 0:
            return jsonify({}), 200

        drugstore = drugstore_result[0]

        drugstore_dict = {'id': drugstore.id, 'name': drugstore.name, 'address': drugstore.address, 'zipcode': drugstore.zipcode, 'latitude': drugstore.latitude,
                          'longitude': drugstore.longitude, 'opening_hours': drugstore.opening_hours, 'business_status': drugstore.business_status,
                          'google_maps_url': drugstore.google_maps_url, 'city_id': drugstore.city_id,
                          'hospitals_nearby': [hospital.id for hospital in drugstore.hospitals_nearby]}

        return jsonify(drugstore_dict), 200
    except Exception:
        return jsonify(error_dict), 500


@app.route("/api/City/all/")
def getAllCities():
    cities_list = list()
    with open('all_cities.txt') as json_file:
        cities_list = json.load(json_file)
    return jsonify(cities_list), 200


@app.route("/api/Hospital/all/")
def getAllHospitals():
    hospitals_list = list()
    with open('all_hospitals.txt') as json_file:
        hospitals_list = json.load(json_file)
    return jsonify(hospitals_list), 200


@app.route("/api/Drugstore/all/")
def getAllDrugstores():
    drugstores_list = list()
    with open('all_drugstores.txt') as json_file:
        drugstores_list = json.load(json_file)
    return jsonify(drugstores_list), 200


@app.route('/Group3/track', methods=['GET', 'POST'])
def group3track():    
    trackList = ['Shape of You', 'Rockstar','One Dance', 'Closer', 'God\'s Plan', 'Thinking Out Loud', 'Sunflower', 'Señorita', 'Perfect', 'Bad Guy', 'Believer', 'Love Yourself', 'Photograph', 'Starboy', 'Lean On', 'Sad!', 'Something Just Like This'] 

    try:
        if trackList is None:
            return jsonify({}), 200

        url = 'http://rockinwiththerona.me/api/tracks?name=%s'
        
        trackLists = []
        for name in trackList:
            cmd = url % (name)
            res = requests.get(cmd)
            res = json.loads(res.content)

            tracks = res['Tracks'] #list

            # for track in tracks:
            track = tracks[0]

            album_name = track['track_album']['album_name']
            track_name = track['track_name']
            track_duration = track['track_duration']
            track_image_url = track['track_image_url']

            track_artists = []

            for artist in track['track_artists']:
                track_artists.append(artist['artist_name'])


            track_dict = {'album_name': album_name, 'track_name': track_name, 'track_duration': track_duration, 'track_image_url': track_image_url, 'track_artists': track_artists}

            trackLists.append(track_dict)

        return jsonify(trackLists), 200

    except Exception as e:
        print("Reached exception ")
        print(list(track_dict))
        return jsonify(error_dict), 500

@app.route('/Group3/artist', methods=['GET', 'POST'])
def group3artist():
    artistList = ['The Weeknd', 'Drake', 'Ariana Grande', 'Justin Bieber', 'Ed Sheeran', 'Lady Gaga', 'Travis Scott', 'J Balvin', 'Post Malone', 'Nicki Minaj', 'Khalid', 'Halsey', 'Marshmello', 'DaBaby', 'Ozuna', 'Maroon 5', 'Beyoncé', 'Billie Eilish', 'Tyga']
    
    try:
        if artistList is None:
            return jsonify({}), 200

        artistLists = []
        for name in artistList:
            url = 'http://rockinwiththerona.me/api/artists?name=%s'
            cmd = url % (name)
            res = requests.get(cmd)
            res = json.loads(res.content)

            artists = res['Artists'] #list

            # for artist in artists:
            artist = artists[0]

            artist_name = artist['artist_name']

            artist_image_url = artist['artist_image_url']
            
            artist_spotify_url = artist['artist_spotify_url']

            artist_genres = []
            for genre in artist['artist_genres']:
                artist_genres.append(genre)

            artist_albums = []
            for artistAlbum in artist['artist_albums']:
                artist_albums.append(artistAlbum['album_name'])
            
            
            artist_dict = {'artist_name': artist_name, 'artist_image_url': artist_image_url, 'artist_spotify_url': artist_spotify_url, 'artist_genres': artist_genres,'artist_albums': artist_albums}

            artistLists.append(artist_dict)

        return jsonify(artistLists), 200

    except Exception as e:
        return jsonify(error_dict), 500

@app.route('/Group3/album', methods=['GET', 'POST'])
def group3album():
    albumList = ['Hollywood\'s Bleeding', 'No.6 Collaborations Project', 'Beerbongs & Bentleys', 'Shawn Mendes', 'Beauty Behind the Madness', '25', 'Stoney', 'Views', 'Starboy', 'Camila', 'Purpose', 'Playlist', 'True', '1989', 'ASTROWORLD', 'After Hours']

    try:
        if albumList is None:
            return jsonify({}), 200

        albumLists = []

        for name in albumList:
        
            url = 'http://rockinwiththerona.me/api/albums?name=%s'

            cmd = url % (name)
            res = requests.get(cmd)
            res = json.loads(res.content)
            albums = res['Albums'] #list

            # for album in albums:
            album = albums[0]

            album_name = album['album_name']
            
            album_image_url = album['album_image_url']
            

            album_genres = []
            for genre in album['album_artists'][0]['artist_genres']:
                album_genres.append(genre)
            
            album_tracks = []
            for track in album['album_tracks']:
                album_tracks.append(track['track_name'])
            
            album_artists = []
            for artist in album['album_artists']:
                album_artists.append(artist['artist_name'])
                    
            album_dict = {'album_name': album_name, 'album_tracks': album_tracks, 'album_genres': album_genres, 'album_image_url': album_image_url,'album_artists': album_artists}

            albumLists.append(album_dict)

        return jsonify(albumLists), 200

    except Exception as e:
        return jsonify(error_dict), 500

@app.route("/")
def serve():
    """serves React App"""
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.debug = True
    os.system('cd react_ver; npm install; npm run build; cd ..')
    app.run()
