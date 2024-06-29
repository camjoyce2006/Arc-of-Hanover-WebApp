# app.py for Bible Verses website
from fileinput import filename
import os, io, psycopg2, random
from sqlalchemy import LargeBinary, select
from flask import Flask, render_template, request, url_for, redirect, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape

from sqlalchemy.sql import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'postgresql://'+\
            os.environ['DB_UN']+':'+\
            os.environ['DB_PW']+\
            '@localhost:5432/'+\
            os.environ['DB']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '23ed506a97fd81899aa1a73a5354095972a6927ff50908e8'


print (f"Connected to database at URI '{app.config['SQLALCHEMY_DATABASE_URI']}'")

"""
$Env:DB = 'arc-volunteer-info'
$Env:DB_UN = 'Cam'
$Env:DB_PW = '12user345'; echo oooo
"""

# Create a Flask app
db = SQLAlchemy(app)

print('Setting app context...')
app_context = app.app_context()
app_context.push()
# db.drop_all()
# print('Dropped all tables')

# A table where all registered Users' information is stored
class User(db.Model):
    """Stores registered users' information
    :attr fname: First name
    :attr lname: Last name
    :attr lname: Full name (First + Last)
    :attr username: 5-digit login code
    :attr is_logged_in: Whether a user is currently logged in
    :attr role: A user's role (Admin/Organizer/Default)
    :attr events_organized: All events organized by a user
    :attr events_attended: All events attended by a user
    :attr events_organized: All events at which a user volunteered
    """
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.Text, nullable=False)
    lname = db.Column(db.Text, nullable=False)
    fullname = db.Column(db.Text, nullable=False)
    username = db.Column(db.Integer, nullable=False)
    is_logged_in = db.Column(db.Boolean, nullable=False, default=False)
    role = db.Column(db.Text, nullable=False, default='Orgnaizer')
    events_organized = db.relationship('Event', backref='user')
    events_attended = db.relationship('Participant', backref='user')
    events_volunteered = db.relationship('Volunteer', backref='user')

    def __repr__(self):
        return f'<User "{self.fullname}">'

# A table where all Events are stored
class Event(db.Model):
    """Stores information about events
    :attr type: The type of event (Volunteer-only/Participate-only/Volunteer or participate)
    :attr event_name: The name of the event
    :attr date: The date on which the event is taking place
    :attr description: optional field describing the event
    :attr volunteers: The list of volunteers at an event
    :attr attendees: The list of attendees of an event
    :attr organizer_id: References the id of the event organizer, whose information is stored in the `User` table
    """
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text, nullable=False)
    event_name = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    volunteers = db.relationship('Volunteer', backref='event')
    attendees = db.relationship('Participant', backref='event')
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Event "{self.event_name[:20]}...">'

# A table where all Volunteers are stored
class Volunteer(db.Model):
    """Stores the list of all event volunteers
    :attr type: The type of event being volunteered at (Thrift Store/Community Event)
    :attr event_id: The id of the event at which the user volunteered
    :attr user_id: the id of the user who volunteered
    """
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Volunteer {self.user_id} volunteered at Event {self.event_id}">'
     
# A table where all event event Participants are stored
class Participant(db.Model):
    """Stores the list of all event attendees
    :attr event_id: The id of the event that the user attended
    :attr user_id: the id of the user who attended the event
    """
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<Participant {self.user_id}.fname participated at Event {self.event_id}.">'

# Global variables to track whether a user is logged in
# If a uer is logged in, their user ID is stored
global isLoggedIn, userID
isLoggedIn = False
"""Whether the user is logged in.
    :`True` if a the user is logged in
    :`False` if the user is logged out
"""
userID = 8
"""The id of the currently logged in user
    :If the user is logged out, `userID` is `None`
"""
# db.create_all()
# print('Successfully created tables')

# user1 = User(id=1, fname='Cameron', lname='Joyce', fullname='Cameron Joyce', username=77121)
# user2 = User(id=2, fname='Taixi', lname='Wang', fullname='Taixi Wang', username=12345)
# user3 = User(id=3, fname='Justin', lname='Biester', fullname='Justin Biester', username=56789)
# db.session.add_all([user2])
# db.session.commit()
# print('Successfully added users to database')

# event1 = Event(type='volunteer-only', event_name='Arc Thrift Store Volunteering', date='2024-06-20', organizer_id=1)
# event2 = Event(type='particiapte-only', event_name='Art Auction', date='2024-06-15', organizer_id=2)
# event3 = Event(type='volunteer-participate', event_name='River City Inclusive Gym', date='2024-06-09', organizer_id=3)
# db.session.add_all([event1, event2, event3])
# print('Successfully added events to database')

# db.session.commit()
# print('Successfully committed to session')

# def queryDB(type, entity, ident, desc):
#     if type == "one":
#        result = db.one_or_404(entity=entity, ident=ident, description=desc)
#     elif type == "get":
#        result = db.get_or_404(entity=entity, ident=ident, description=desc)
#     elif type == "select":
#         result = db.session.execute(select(entity).where(entity.id == ident))
#     return result

# def addItem(item):
#     db.session.add(item)
#     db.session.commit()

# def updateItem(entity, id):
#     return

# events = Event.query.all() #db.session.execute(select(Event)).fetchall()
# for event in events:
#     print(f"Event name: {event.event_name}")
#     print(f"Event date: {event.date}")
#     print(f"# of Volunteers: {len(event.volunteers)}")
#     event.description = "test success"
#     db.session.commit()
# print(User.query.get_or_404(2).fullname)

# Home page that displays all the events
@app.route('/')
def index():
    print(isLoggedIn, userID)
    events = Event.query.all()
    print(1)
    user = User.query.get_or_404(userID)
    print(user.id)
    return render_template('index.html', events=events, users=User, user=user, status=isLoggedIn, user_id=userID)

# The user's home page where they can find all the events they have created
@app.route('/home/<int:user_id>')
def home(user_id):
    events = Event.query.all()
    user = User.query.get_or_404(user_id)
    return render_template('home.html', users=User, events=events, volunteers= Volunteer, events2=Event, user=user, status=isLoggedIn, user_id=userID)

# Allows users to sign up for an account
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        fullname=f"{fname} {lname}"

        username = random.randint(10000, 99999)

        # Creates a new user and adds it to the User table
        new_user = User(fname=fname,
                        lname=lname,
                        fullname=fullname,
                        username=username,
                        role="Organizer")
        
        db.session.add(new_user)

        # Redirects the user to the login page
        return redirect(url_for('login', welcome_message=f'Congratulations, {fname}! Your username is {username}.'))
    
    return render_template('signup.html', user_id=userID)

# Allows registered users to log in to their account
@app.route('/login', methods=['GET', 'POST'])
def login():    
    print('loaded login page')
    if request.method == 'POST':
        uname = request.form['uname']
        
        # Checks that a username was entered
        if uname == '':
            flash('Enter your username to login')
        
        # User authentication checks
        users = User.query.all()
        for user in users:  
            print(f"{user.fullname}\nLogged In? {user.is_logged_in} {user.username}") 
            if user.username == int(uname):
            # Checks if username and password match in the database, doesn't check user 0 because there is no User 0
                global isLoggedIn, userID
                isLoggedIn = True
                userID = user.id
                user.is_logged_in = True
                db.session.commit()       
                print(f"User '{user.fullname}' Successfully logged into their account")
                return redirect(url_for('index'))
            # Notifies unregistered users to sign up for an account
            else:
                flash(f'No user with username \'{uname}\' is in our records. Please sign up for an account below.')
    
    return render_template('login.html', user_id=userID, status=False)

# Allows a user to sign out, resets the global variables
@app.route('/signout', methods=['GET', 'POST'])
def signout():
    global isLoggedIn, userID
    isLoggedIn = False
    userID = 8
    if request.method == 'POST':
        user = User.query.get_or_404(userID)
        user.is_logged_in = False
        db.session.commit()
    return redirect(url_for('index'))

# Allows a user to view the details of an event
@app.route('/event/<int:event_id>')
def event(event_id):
    user = User.query.get_or_404(userID)
    event = Event.query.get_or_404(event_id)
    return render_template('event.html', users=User, event=event, user=user, user_id=userID)

# Allows a user to save new events
@app.route('/create/<int:user_id>', methods=['GET', 'POST'])
def create(user_id):
    if request.method == 'POST':
        event_name = request.form['event-name']
        date = request.form['date']
        type = request.form['event-type']
        desc = request.form['desc']

        # Creates a new event and adds it to the Event table
        event = Event(event_name=event_name,
                    date=date,
                    type=type,
                    description=desc,
                    organizer_id=user_id)

        db.session.add(event)

        #Redirects the user to the home page
        return redirect(url_for('index'))
    return render_template('create_event.html', user_id=user_id)

# Allows users to edit events they have created
@app.route('/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    organizer = User.query.get_or_404(event.organizer_id)
    if request.method == 'POST':   
        event_name = request.form['event-name']
        date = request.form['date']
        type = request.form['event-type']
        desc = request.form['desc']

        # Updates necessary fields in table entry
        event.type = type
        event.event_name = event_name
        event.date = date
        event.description = desc
        
        db.session.add(event)
        db.session.commit()

        #Redirects the user to the home page
        return redirect(url_for('index'))
    return render_template('edit_event.html', event=event, organizer=organizer, user_id=userID)

# Allows users to delete events they have created
@app.post('/delete/<int:event_id>')
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('index'))

# Allows users to sign up to volunteer 
@app.route('/volunteer/<int:event_id>')
def volunteer(event_id):
    if isLoggedIn == True:
        volunteer = Volunteer(type='Thrift Store', event_id=event_id, user_id=userID)

        db.session.add(volunteer)
        db.session.commit()
    return redirect(url_for('index'))

# Allows users to RSVP up to attend an event 
@app.route('/attend/<int:event_id>')
def attend(event_id):
    if isLoggedIn == True:
        participant = Participant(event_id=event_id, user_id=userID)

        db.session.add(participant)
        db.session.commit()
    return redirect(url_for('index'))
# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)