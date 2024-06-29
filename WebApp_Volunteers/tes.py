from app import User as us
from app import Event as ev
from app import Volunteer as vt
from app import Participant as pt
from app import signout, signup, login

import os

from sqlalchemy import select, update, delete
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

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
print('App context. Now working in app context')

global userID, isLoggedIn
userID = 1
isLoggedIn = True

user = db.session.execute(select(us.fullname, us.id, us.is_logged_in, us.role).where(us.id == userID))
user = user.first()
print(user)
print(user.role)
db.session.execute(update(us)
                   .where(us.id == user.id)
                   .values(is_logged_in=True))
print(user.is_logged_in)
db.session.commit()

global eventData
eventData = db.session.execute(
                        select(
                            ev.id,
                            ev.event_name,
                            ev.date,
                            ev.organizer_id,
                            ev.description,
                            us.fullname.label("organizer_name"))
                                .select_from(ev)
                                .join(us)
                        )
# print(events.all())
global eventArray
eventArray = []
for event in eventData.all():
    print(event)
    print(f"Event name: {event.event_name}")
    print(f'Date: {event.date.strftime("%x")}')
    print(f'Organizer: {event.organizer_name}')
    eventArray.append({
        "event_id": event.id,
        "event_name": event.event_name,
        "date": event.date.strftime("%x"),
        "description": event.description,
        "organizer_id": event.organizer_id,
        "organizer_name": event.organizer_name
    })

print(eventArray)
@app.route('/')
def index():
    events = eventArray
    print(events)
    return render_template('index2.html', user_id=userID, user=user, events=events, status=isLoggedIn)

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)