from flask import Flask, request, Blueprint,  render_template, session, url_for
from flask_mysqldb import MySQLdb, MySQL
from flask_bcrypt import Bcrypt
from werkzeug.utils import redirect

admin = Blueprint('admin', __name__)

app = Flask(__name__)

app.secret_key = "alpr"
bcrypt = Bcrypt(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@admin.route("/user", methods=["GET", "POST", "PUT", "DELETE"])
def list_user():
    if session.get('logged_in') and session.get('privilege') == '1':
        if request.method == "GET":
            data = {}
            curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curl.execute("SELECT * FROM users order by created_at")
            data['users'] = curl.fetchall()
            data['title'] = "Management Users"
            curl.close()
            return render_template('admin/view_list_user.html', data=data)
        if request.method == "POST":
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            email = request.form['email']
            check = cur.execute("select * from users where email = '"+email+"'" )
            if check:
                data = {'status': 0, 'message': 'Email already taken'}
                return data
            fname = request.form['fname']
            lname = request.form['lname']
            password = request.form['password']
            privilege = request.form['user_role']
            hash_password = bcrypt.generate_password_hash(password).decode('utf-8')

            insert = cur.execute("INSERT INTO users (privilege, fname, lname, email, password) VALUES (%s,%s,%s,%s,%s)",(privilege, fname,lname,email,hash_password,))
            
            mysql.connection.commit()
            if insert:
                data = {'status': 1, 'message': 'User created successfully.'}
                return data
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
            password = request.form['password']
            privilege = request.form['user_role']
            if request.form['password']:
                hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
                update = cur.execute("UPDATE users SET privilege=%s, fname=%s, lname=%s, email=%s, password=%s where id = %s",(privilege, fname,lname,email,hash_password, id))
            else:
                update = cur.execute("UPDATE users SET privilege=%s, fname=%s, lname=%s, email=%s where id = %s",(privilege, fname,lname,email, id))
            mysql.connection.commit()
            if update:
                data = {'status': 1, 'message': 'User has been updated successfully.'}
                return data
        if request.method == "DELETE":
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            id = request.form['id']
            delete = cur.execute("DELETE FROM users where id = "+id+"")
            mysql.connection.commit()
            if delete:
                data = {'status': 1, 'message': 'User has been deleted successfully.'}
                return data
    else:
        return redirect(url_for('logout'))


@admin.route("/user/<id>", methods=["GET"])
def user_detail(id):
    if session.get('logged_in') and session.get('privilege') == '1':
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT id, fname, lname, email, privilege FROM users where id = "+id+"")
        details = curl.fetchone()
        curl.close()
        return details
    else:
        return redirect(url_for('logout'))

@admin.route("/app", methods=["GET", "POST"])
def list_app():
    if session.get('logged_in') and session.get('privilege') == '1':
        data = {}
        data['title'] = "Management Apps"
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT apps.*, lname, fname FROM apps left join users on users.id = apps.user_id")
        data['apps'] = curl.fetchall()
        return render_template('admin/view_list_app.html', data=data)
    else:
        return redirect(url_for('logout'))
