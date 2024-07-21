
from flask import session
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
from flask import flash

from datetime import date as dt

import random

from config import DEV_PORT
import helpers

from forms import SignUpForm
from forms import AdminSignUpForm
from forms import LoginForm
from forms import EditUserForm
from forms import EditUserAdminForm
from forms import CreateEventForm
from forms import EditEventForm

from datastructure import app, db
from datastructure import User
from datastructure import Event 
from datastructure import Volunteer 
from datastructure import Participant

# Global variables to track whether a user is logged in
# If a user is logged in, their user ID is stored
global today
today = dt.today()
"""Today's date"""

@app.before_request
def log_request(toPrint=True):
    # if not session.get('initialization_done'):
    #     print('Initializing app...')
    #     session_info = helpers.update_session('first', 8)
        
    not_run = ['static', 'volunteer', 'unvolunteer', 'attend', 'unattend']
    if request.endpoint not in not_run:
        helpers.update_session('page', session.get('user_id'), request.endpoint)
        session_info = helpers.get_session_info()
        if toPrint:
            for key, value in session_info.items():
                print(f'{key}: {value}')

    message = f"User \'{session.get('username')}\' "
    messages = {
        "index": "went home.",
        "home": "viewed their home dashboard.",
        "create": {
                "GET": "began creating an event.",
                "POST": "created an event."
            },
        "edit_event": {
                "GET": f"began editing an event.",
                "POST": "confirmed edits to an event."
            },
        "delete_event": "deleted an event.",
        "event": "viewed an event page.",
        "signup": {
                "GET": "began account creation.",
                "POST": "is new to AVA. Welcome!"
            },
        "login": {
                "GET": "wants to log in.",
                "POST": "successfully logged in."
            },
        "signout": "logged off.",
        "volunteer": "signed up to volunteer at an event.",
        "unvolunteer": "is no longer volunteering at an event.",
        "attend": "RSVP'ed to attend an event.",
        "unattend": "un- RSVP'ed to attend an event.",
    }

    if session.get('user_id') and request.endpoint != 'static':
        if request.endpoint in messages.keys():
            if type(messages[request.endpoint]) is dict:
                message += messages[request.endpoint][request.method]
            else:
                message += messages[request.endpoint]
        elif request.endpoint not in not_run:
            message += f"accessed endpoint \'{request.endpoint}\'"
        else:
            message += "took an unloggable action."
        
        helpers.logEvents('all', 'i', message)

def render_page(template, status=None, **context):
    if not status:
        status = session.get('is_logged_in')
    if 'event_id' not in context:
        context.update({'event_id': None})
    return render_template(template,
                           users=User, 
                           v=Volunteer, 
                           p=Participant, 
                           ev=Event, 
                           status=status, 
                           user_id=session.get('user_id'),
                           user=helpers.get_session_info('user'),
                           prev_page=session.get('previous_page'),
                           today=today,
                           **context)

def redirect_current(**values):
    return redirect(url_for(session.get('current_page'), **values))

# Home page that displays all the events
@app.route('/')
def landing():
    return redirect(url_for('index'))

@app.route('/dashboard')
def index():
    all_events = Event.query.order_by(Event.date.desc()).all()
    events = [event for event in all_events if event.date >= today]
    return render_page('index.html',
                       events=events,
                       all_events=all_events)

# The user's home page where they can find all the events they have created
@app.route('/user-dashboard/')
def home():
    events = Event.query.all()
    return render_page('home.html', events=events)

# Allows users to sign up for an account
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('is_logged_in') and helpers.get_session_info('user').role.code == 'admin':
        form = AdminSignUpForm()
    else:
        form = SignUpForm()
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        fullname=f"{fname} {lname}"

        userkeys = [user.username for user in User.query.all()]
        username = random.randint(10000, 99999)
        while username in userkeys:
            username = random.randint(10000, 99999)
        
        helpers.update_db(User, User(), request.form, add=True,
                          fullname=fullname, username=username)

        # Redirects the user to the login page
        return redirect(url_for('login', 
                                welcome_message=f'Congratulations, {fname}! Your username is {username}.'))
    
    return render_page('form_default.html', status=False, form=form)

# Allows registered users to log in to their account
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()    
    if request.method == 'POST':
        uname = request.form['uname']

        # User authentication checks
        user = User.query.filter_by(username=int(uname)).first()
        if user:   
            print(f"User '{user.fullname}' Successfully logged into their account")
            helpers.update_session('login', user.id)
            return redirect(url_for('index'))
        else:
            # Notifies unregistered users to sign up for an account
            flash(f'That username is not registered in our records. Please sign up for an account below.')
    
    return render_page('form_default.html', 
                       status=False, 
                       form=form)

# Allows a user to sign out, resets the global variables
@app.route('/signout', methods=['GET', 'POST'])
def signout():
    helpers.update_session(action='signout', user_id=8)
    return redirect(url_for('index'))

@app.route('/edituser', methods=['GET', 'POST'])
def edit_user():
    user = helpers.get_session_info('user')
    print(user)
    if user.role.code == 'admin':
        form = EditUserAdminForm()
    else: 
        form = EditUserForm()
    form(user)
    if request.method == 'POST':

        helpers.update_db(User, user, request.form)

    return render_page('form_default.html', form=form)

@app.route('/deluser')
def delete_user():
    user = helpers.get_session_info('user')
    for v in user.events_volunteered:
        db.session.delete(v)

    for p in user.events_attended:
        db.session.delete(p)

    for e in user.events_organized:
        db.session.delete(e)

    db.session.delete(user)
    db.sesion.commit()

# Allows a user to view the details of an event
@app.route('/event/<int:event_id>')
def event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    return render_page('event.html', event=event)

# Allows a user to save new events
@app.route('/create/', methods=['GET', 'POST'])
def create():
    form = CreateEventForm()
    form(session.get('username'))
    if request.method == 'POST':
        organizer_id = User.query.filter_by(fullname=request.form['organizer_name']).first().id

        helpers.update_db(Event, Event(), request.form, add=True, organizer_id=organizer_id)

        #Redirects the user to the previous page
        return redirect(url_for(session.get('previous_page')))
    return render_page('form_default.html', form=form)

# Allows users to edit events they have created
@app.route('/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    organizer = User.query.filter_by(id=event.organizer_id).first()
    form = EditEventForm()
    form(event)
    if request.method == 'POST':
        organizer_id = User.query.filter_by(fullname=request.form['organizer_name']).first().id

        helpers.update_db(Event, event, request.form, organizer_id=organizer_id)
            
        #Redirects the user to the home page
        return redirect(url_for(session.get('previous_page'), event_id=event_id))
    return render_page('form_default.html',
                           form=form,
                           event=event,
                           organizer=organizer,
                           event_id=event_id)

# Allows users to delete events they have created
@app.route('/delete_event/<int:event_id>', methods=['GET', 'POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for(session.get('previous_page'), event_id=event_id))

# Allows users to sign up to volunteer 
@app.route('/volunteer/<int:event_id>')
def volunteer(event_id):
    if session.get('is_logged_in') == True:
        event = Event.query.filter_by(id=event_id).first()
        volunteer = Volunteer(type=event.volunteer_type, event_id=event_id, user_id=session.get('user_id'))

        db.session.add(volunteer)
        db.session.commit()
    return redirect(url_for(session.get('current_page'), event_id=event_id))

@app.route('/unvolunteer/<int:event_id>', methods=['GET', 'POST'])
def unvolunteer(event_id):
    vol = Volunteer.query.get_or_404(event_id)
    db.session.delete(vol)
    db.session.commit()
    return redirect(url_for(session.get('current_page'), event_id=event_id))

# Allows users to RSVP up to attend an event 
@app.route('/attend/<int:event_id>')
def attend(event_id):
    if session.get('is_logged_in') == True:
        participant = Participant(event_id=event_id, 
                                  user_id=session.get('user_id'))

        db.session.add(participant)
        db.session.commit()
    return redirect(url_for(session.get('current_page'), event_id=event_id))

@app.route('/unattend/<int:event_id>', methods=['GET', 'POST'])
def unattend(event_id):
    attendee = Participant.query.get_or_404(event_id)
    db.session.delete(attendee)
    db.session.commit()
    return redirect(url_for(session.get('current_page'), event_id=event_id))

@app.route('/viewtable', methods=['GET', 'POST'])
def view_all():
    if request.method == 'POST':
        print('Post')
        tablename = request.form['tablename']

        return redirect(url_for('view_table', tablename=tablename))
    return render_page('view_all.html', model=None)


@app.route('/viewtable/<tablename>')
def view_table(tablename):
    if tablename == 'event':
        model = Event
    if tablename == 'user':
        model = User

    return render_page('view_all.html', model=model)
        
@app.errorhandler(404)
def error_404(e):
    return render_template('error_404.html', 
                           user=helpers.get_session_info('user'), 
                           status=session.get('is_logged_in'), 
                           user_id=session.get('user_id'))

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=DEV_PORT)