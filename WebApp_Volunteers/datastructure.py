# app.py for Arc Volunteer Web App
from config import USER_ROLES as ROLES
from config import EVENT_TYPES as E_TYPES
from config import VOLUNTEER_TYPES as V_TYPES
from config import GENDERS
from config import FlaskAppDB

from datetime import datetime as dt
from sqlalchemy_utils import ArrowType, EmailType, ChoiceType

flask = FlaskAppDB('Test-App')
app = flask.app

# Create a SQLAlchemy database session with the app
db = flask.database

print(
    f"name: {flask.name}\n \
    URI: {flask.uri}\n \
    app: {flask.app.import_name}\n \
    db: {flask.database}")

# A table where all registered Users' information is stored
class User(db.Model):  
    """Stores registered users' information
    :attr: `fname`: First name
    :attr: `lname`: Last name
    :attr: `lname`: Full name (First + Last)
    :attr `username`: 5-digit login code
    :attr `email`: A user's email address
    :attr `is_logged_in`: Whether a user is currently logged in
    :attr `role`: A user's role (Admin/Organizer/Default)
    :attr `events_organized`: All events organized by a user
    :attr `events_attended`: All events attended by a user
    :attr `events_volunteered`: All events at which a user volunteered
    """
    # __table_args__ = dict(schema=schema)
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=dt.now())
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    gender = db.Column(ChoiceType(GENDERS), default='nosay')
    username = db.Column(db.Integer, nullable=False, unique=True)
    
    email = db.Column(EmailType)
    address = db.Column(db.String(255))
    is_idd = db.Column(db.Boolean, nullable=False, default=False)
    has_bkg_check = db.Column(db.Boolean, nullable=False, default=False)
    open_to_check = db.Column(db.Boolean, nullable=False, default=False)
    has_volunteer_form = db.Column(db.Boolean, nullable=False, default=False)

    is_logged_in = db.Column(db.Boolean, nullable=False, default=False)
    role = db.Column(ChoiceType(ROLES), nullable=False, default='default')

    events_organized = db.relationship('Event', backref='user')
    events_attended = db.relationship('Participant', backref='user')
    events_volunteered = db.relationship('Volunteer', backref='user')

    def __repr__(self):
        return f'<User "{self.fullname}">'

# A table where all Events are stored
class Event(db.Model):
    """Stores information about events
    :attr `type`: The type of event (Volunteer-only/Participate-only/Volunteer or participate)
    :attr `event_name`: The name of the event
    :attr `date`: The date on which the event is taking place
    :attr `description`: optional field describing the event
    :attr `organizer_id`: The `id` of the event organizer, whose information is stored in the `User` table
    :attr `volunteers`: The list of volunteers at an event
    :attr `attendees`: The list of attendees of an event
    """
    # __table_args__ =dict(schema=schema)
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=dt.now())
    
    event_type = db.Column(ChoiceType(E_TYPES), nullable=False)
    volunteer_type = db.Column(ChoiceType(V_TYPES), nullable=False, default='none')

    event_name = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    organizer_name = db.Column(db.String(50))

    volunteers = db.relationship('Volunteer', backref='event')
    attendees = db.relationship('Participant', backref='event')

    def __repr__(self):
        return f'<Event "{self.event_name[:20]}...">'

# A table where all Volunteers are stored
class Volunteer(db.Model):
    """Stores the list of all event volunteers
    :attr `type`: The type of event being volunteered at (Thrift Store/Community Event)
    :attr `event_id`: The `id` of the event at which the user volunteered
    :attr `user_id`: the `id` of the user who volunteered
    """
    # __table_args__ =dict(schema=schema)
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(ChoiceType(V_TYPES), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    time_in = db.Column(ArrowType)
    time_out = db.Column(ArrowType)

    def __repr__(self):
        return f'<Volunteer {self.user_id} volunteered at Event {self.event_id}">'
     
# A table where all event event Participants are stored
class Participant(db.Model):
    """Stores the list of all event attendees
    :attr `event_id`: The `id` of the event that the user attended
    :attr `user_id`: the `id` of the user who attended the event
    """
    # __table_args__ =dict(schema=schema)
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<Participant {self.user_id}.fname participated at Event {self.event_id}.">'

# flask.init_db(drop=False)

users = [
    User(id=1, fname='Cameron', lname='Joyce', fullname='Cameron Joyce', username=77121, role='organizer'),
    User(id=2, fname='Taixi', lname='Wang', fullname='Taixi Wang', username=12345, role='organizer'),
    User(id=3, fname='Marty', lname='Wilson', fullname='Marty Wilson', username=56789, role='admin'),
    User(id=4, fname='Sherri', lname='Lanning', fullname='Sherri Lanning', username=34567, role='store-manager'),
    User(id=8, fname='Default', lname='User', fullname='Default User', username=70964),
    User(id=9, fname='Admin', lname='Account', fullname='Admin Account', username=58354, role='admin')
]

events = [
    Event(event_type='volunteer-only', volunteer_type='thrift', event_name='Arc Thrift Store Volunteering', date='2024-06-20', organizer_id=1),
    Event(event_type='participate-only', volunteer_type='community', event_name='Art Auction', date='2024-06-15', organizer_id=2),
    Event(event_type='volunteer-participate', volunteer_type='none', event_name='River City Inclusive Gym', date='2024-06-09', organizer_id=3),
    Event(event_type='volunteer-only', volunteer_type='thrift', event_name='Volunteering', date='2024-07-20', organizer_id=1)
]

# flask.init_db(create=True, drop=True, insert=True, users=users, events=events)
# with flask.app_context:
#     print(f'Users: {User.query.count()}')
#     print(f'Events: {Event.query.count()}')
flask.set_app_context()