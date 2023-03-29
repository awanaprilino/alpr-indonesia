from flask import Flask, request, Blueprint,  render_template, session, url_for
from flask_mysqldb import MySQLdb, MySQL
from flask_bcrypt import Bcrypt
from werkzeug.utils import redirect
import shortuuid

user = Blueprint('user', __name__)

app = Flask(__name__)

app.secret_key = "alpr"
bcrypt = Bcrypt(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@user.route("/profile", methods=["GET", "PUT"])
def profile():
    if session.get('logged_in') and session.get('privilege') == '0':
        if request.method == "GET":
            data = {}
            curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curl.execute("SELECT * FROM users where email='"+session.get('email')+"'")
            data['users'] = curl.fetchone()
            data['title'] = "Edit Profile"
            curl.close()
            return render_template('user/profile.html', data=data)
    if request.method == "PUT":
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            email = request.form['email']
            id = request.form['id']
            check = cur.execute("select * from users where id <> "+id+" AND email = '"+email+"'" )
            if check:
                data = {'status': 0, 'message': 'Email already taken'}
                return data
            fname = request.form['fname']
            lname = request.form['lname']
            password = request.form['new_password']
            if password:
                hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
                update = cur.execute("UPDATE users SET fname=%s, lname=%s, email=%s, password=%s where id = %s",(fname,lname,email,hash_password, id))
            else:
                update = cur.execute("UPDATE users SET fname=%s, lname=%s, email=%s where id = %s",(fname,lname,email, id))
            mysql.connection.commit()
            if update:
                session['email'] = email
                session['fname'] = fname
                session['lname'] = lname
                data = {'status': 1, 'message': 'User has been updated successfully.'}
                return data
            else:
                data = {'status': 0, 'message': 'Nothing Changed.'}
                return data

@user.route("/app", methods=["GET", "POST"])
def apps():
    if request.method == "POST":
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users where email='"+session.get('email')+"'")
        users = curl.fetchone()
        app_name = request.form['app_name']
        token = shortuuid.uuid()
        user_id = users['id']
        insert = curl.execute("INSERT INTO apps (user_id, app_name, token) VALUES (%s,%s,%s)",(user_id, app_name,token))
        mysql.connection.commit()
        if insert:
            data = {'status': 1, 'message': 'App has been created successfully.'}
            return data

@user.route("/app/detail/<id>", methods=["GET", "POST"])
def detail_app(id):
    data = {}
    if request.method == "GET":
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM apps where id=%s", (id, ))
        apps = curl.fetchone()
        data['title'] = apps['app_name'] + " App"
        data['token'] = apps['token']
        data['app_id'] = id
        curl.execute("SELECT * FROM license_plate where app_id=%s", (id, ))
        data['licens_plate'] = curl.fetchall()
        curl.close()
        return render_template('user/app.html', data=data)

@user.route("/app/api/<id>", methods=["GET", "POST"])
def detail_api(id):
    data = {}
    if request.method == "GET":
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM apps where id=%s", (id, ))
        apps = curl.fetchone()
        data['title'] = apps['app_name'] + " Api"
        data['token'] = apps['token']
        data['app_id'] = id
        curl.close()
        return render_template('user/api.html', data=data)

@user.route("/app/setting/<id>", methods=["GET", "DELETE"])
def setting_app(id):
    data = {}
    if request.method == "GET":
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM apps where id=%s", (id, ))
        apps = curl.fetchone()
        data['title'] = apps['app_name'] + " Api"
        data['token'] = apps['token']
        data['app_id'] = id
        curl.close()
        return render_template('user/setting.html', data=data)
    else:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        delete = cur.execute("DELETE FROM apps where id = "+id+"")
        mysql.connection.commit()
        if delete:
            data = {'status': 1, 'message': 'App has been deleted successfully.'}
            return data

@user.route('/plate', methods=["PUT", "POST", "DELETE"])
def crud_plate():
    if request.method == "PUT":
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        plate_number = request.form['plate_number']
        id = request.form['plate_id']
        update = cur.execute("UPDATE license_plate SET plate_number=%s where id = %s",(plate_number, id))
        mysql.connection.commit()
        if update:
            data = {'status': 1, 'message': 'Plate Number has been updated successfully.'}
            return data
    if request.method == "DELETE":
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            id = request.form['id']
            delete = cur.execute("DELETE FROM license_plate where id = "+id+"")
            mysql.connection.commit()
            if delete:
                data = {'status': 1, 'message': 'Plate number has been deleted successfully.'}
                return data