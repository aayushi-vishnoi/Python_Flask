from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable = False)
    lastname = db.Column(db.String(100), nullable = False)
    username = db.Column(db.String(100), nullable = False, unique=True)
    password = db.Column(db.String(100), nullable = False)

    def __init__(self,username,password,firstname,lastname):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))
    
with app.app_context():
    db.create_all()



@app.route('/')
def index():
    return 'hi'

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['firstname'] = user.firstname
            session['lastname'] = user.lastname
            session['username'] = user.username
            session['password'] = user.password

            redirect('/dashboard')
        else:
            render_template('login.html', error='Invalid user!')
    return render_template('login.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form["fname"]
        lname = request.form["lname"]
        username = request.form["username"]
        password = request.form["password"]
        new_user = Users(firstname=fname, lastname=lname, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect("login")

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if session['firstname']:
        user = Users.query.filter_by(username=session['username']).first()
        return render_template('dashboard.html',user=user)
    else:
        redirect('/login')

@app.route('/logout')
def logout():
    session.pop('username')
    redirect('/login')
        
if __name__ == '__main__':
    app.run(debug=True)