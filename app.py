import geocoder
from geopy import distance
import datetime
import calendar
import sqlite3
from functools import wraps

from flask import Flask, render_template, request, redirect, session, flash, get_flashed_messages

from werkzeug.security import check_password_hash, generate_password_hash

appm = Flask(__name__)
appm.secret_key = 'tajny-klucz-9523'


def get_connection():
    conn = sqlite3.connect('baza.db')
    conn.row_factory = sqlite3.Row
    return conn


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session:
            return view(*args, **kwargs)
        else:
            return redirect('/login')

    return wrapped_view


@appm.route('/rideadded')
@login_required
def dodano():
    return render_template('rideadded.html')


@appm.route('/')
@login_required
def index():
    id = session.get('user_id')
    username = session.get('username')
    conn = get_connection()
    c = conn.cursor()

    result = c.execute('SELECT * FROM "rides"')
    rides = result.fetchall()

    rslt = c.execute('SELECT sum(km) from "rides" ')
    sum = rslt.fetchone()

    average = c.execute('SELECT avg(km) from "rides"')
    avg = average.fetchone()

    context = {'rides': rides,'sum1': "{0:.0f}".format(sum[0]), 'avg1': "{0:.2f}".format(avg[0])}

    return render_template('index.html', **context)


@appm.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        messages = get_flashed_messages()
        return render_template('register.html', messages=messages)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        company = request.form['company']

        conn = get_connection()
        c = conn.cursor()
        hashed_password = generate_password_hash(password)
        result = c.execute('INSERT INTO users(username, password, company) VALUES (?, ?, ?)',
                           (username, hashed_password, company))
        user_data = result.fetchall()
        conn.commit()

        return render_template('register.html')


@appm.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        messages = get_flashed_messages()
        return render_template('login.html', messages=messages)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_connection()
        c = conn.cursor()

        result = c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_data = result.fetchone()

        if user_data:
            hashed_password = user_data['password']

            if check_password_hash(hashed_password, password):  # tu jest różnica
                session['user_id'] = user_data['id']
                session['username'] = user_data['username']

            return redirect('/')

        flash('błędna nazwa użytkownika lub hasło')
        return redirect('/login')


@appm.route('/addride', methods=['GET', 'POST'])
@login_required
def dodaj():
    id = session.get('user_id')
    username = session.get('username')
    company1 = session.get('company')
    if request.method == 'GET':
        return render_template('addride.html')

    if request.method == 'POST':
        start = request.form['start']
        koniec = request.form['koniec']
        id_uz = id
        nazwa = username
        comp = company1

        punkt_pocz = geocoder.osm(start)
        punkt_kon = geocoder.osm(koniec)
        punkt1 = punkt_pocz.osm
        punkt2 = punkt_kon.osm
        wsp1 = [punkt1["x"], punkt1["y"]]
        wsp2 = [punkt2["x"], punkt2["y"]]

        odl = round(distance.distance(wsp1, wsp2).kilometers)
        conn = get_connection()
        c = conn.cursor()

        zapytanie = 'INSERT INTO "rides" ( "user_id", "name","company", "date", "km") VALUES (?,?, ?,?, ?)'

        d = datetime.date.today()

        parametry = (id_uz, nazwa, comp, d, odl)



        c.execute(zapytanie, parametry)
        conn.commit()
        flash('The ride has been added.')

        return redirect('/rideadded')


@appm.route('/yourrides')
@login_required
def yourrides():
    id = session.get('user_id')
    username = session.get('username')
    conn = get_connection()
    c = conn.cursor()

    result = c.execute('SELECT * FROM "rides" where user_id =?', (id,))
    myrides = result.fetchall()

    context = {'id': id, 'username': username, 'myrides': myrides}

    return render_template('yourrides.html', **context)


@appm.route('/leaderboard')
@login_required
def leaderboard():
    id = session.get('user_id')
    username = session.get('username')
    conn = get_connection()
    c = conn.cursor()

    result = c.execute('SELECT user_id, name, sum(km)AS km FROM "rides" GROUP BY user_id ORDER BY sum(km) DESC')
    allrides = result.fetchall()

    context = {'id': id, 'username': username, 'allrides': allrides}

    return render_template('leaderboard.html', **context)


@appm.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    appm.run(debug=True)
