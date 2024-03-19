from flask import Flask, request, redirect, session
from flask import render_template
from cryptography.fernet import Fernet
from flask_session import Session
from flask import flash
import requests

from functions import load_config_from_json

endpoint='http://127.0.0.1:8000'
app = Flask(__name__)

load_config_from_json(app, 'config.json')
Session(app)

title = app.config.get('TITLE')
if not app.config.get('SECRET_KEY'):
    secret_key = Fernet.generate_key()
else:
    secret_key = app.config.get('SECRET_KEY')


@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def index():

    if 'id' not in session:
        session['id'] = None

    if request.method == "POST":
        if request.args.get("logout") == "salir":
            session['id'] = None
            session.clear()
            return redirect("/")

        username  = request.form["username"]
        password  = request.form["password"]

        response = requests.get(f'{endpoint}/users/{username}')

        if response.status_code == 200:
            user = response.json()

            if user['password'] == password:
                session["id"] = user['id']
                return redirect("lista_album")
            else:
                flash('Contraseña Incorrecta', 'password')
        else:
            flash("Usuario Incorrecto","user")

    if session["id"] is None:
        return render_template("index.html")
    else:
        return redirect("lista_album")



@app.route('/lista_album', methods=['GET', 'POST'])
def lista_album():
    response = requests.get(f'{endpoint}/album/')
    albums = response.json()

    response = requests.get(f'{endpoint}/artist/')
    artists = response.json()

    return render_template('lista_album.html', albums=albums, artists=artists)



@app.route('/filtrar_album', methods=['GET', 'POST'])
def filtrar_album():
    if request.method == 'POST':
        artist_id = request.form.get('artist')
    else:
        artist_id = 1 

    response = requests.get(f'{endpoint}/album/{artist_id}')
    albums = response.json()

    response = requests.get(f'{endpoint}/artist/')
    artists = response.json()

    return render_template('filtrar_album.html', albums=albums, artists=artists, artist_id=artist_id)




@app.route('/editar_album/<int:albumid>/<int:artistid>/', methods=['GET', 'POST'])
def editar_album(albumid, artistid):
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']

        album_data = {'Title': title, 'ArtistId': artist}
        response = requests.put(f'{endpoint}/album/{albumid}', json=album_data)

        if response.status_code == 200:
            return redirect('/lista_album')
        else:
            return 'Error al actualizar el álbum', 400

    else:
        response = requests.get(f'{endpoint}/album/one_album/{albumid}')
        album = response.json()

        response = requests.get(f'{endpoint}/artist/')
        artists = response.json()

        return render_template('editar_album.html', album=album, artists=artists, artist_id=artistid)




@app.route('/agregar_album', methods=['GET', 'POST'])
def agregar_album():
    if request.method == 'POST':

        title = request.form['title']
        artistId = request.form['artist']

        data = {
            'Title': title,
            'ArtistId': artistId
        }

        response = requests.post(f'{endpoint}/album', json=data)


        if response.status_code == 200:
            return redirect('/lista_album')
        else:
            return 'Hubo un error al agregar el álbum', 400
    else:
        response = requests.get(f'{endpoint}/artist/')
        artists = response.json()
        return render_template('agregar_album.html', artists=artists)
    

@app.route('/deletealbum/<int:albumId>', methods=['POST'])
def delete_album(albumId):

    response = requests.delete(f'{endpoint}/album/{albumId}')


    if response.status_code == 200:
        return redirect('/lista_album')
    else:
        return 'Hubo un error al eliminar el álbum', 400


@app.route('/registrar_user', methods=['GET', 'POST'])
def registrar_user():
    if request.method == 'POST':

        username = request.form['username']
        fullname = request.form['fullname']
        password = request.form['password']

        data = {
            'username': username,
            'fullname': fullname,
            'password' : password
        }

        response = requests.post(f'{endpoint}/users', json=data)

        if response.status_code == 200:
            return redirect('/')
        else:
            return 'Hubo un error al agregar el álbum', 400
    else:
        return render_template('registrar_user.html')


if __name__ == '__main__':
    app.run(debug=False)