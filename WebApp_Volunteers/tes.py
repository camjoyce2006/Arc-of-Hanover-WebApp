# from config import make_app 
import config

from datastructure import app as a, db as d
from datastructure import User as us
from datastructure import Event as ev
from datastructure import Volunteer as v
from datastructure import Participant as p

from sqlalchemy import select, update
from flask import Flask, render_template

class DBTest:
    # def make_app ():
    #     app = Flask(__name__)
    #     return app
    
    def init(app):

        app, URI = config.make_app()
        if URI:
            print (f"Connected to database at URI '{URI}'")


    def db_join_test():
        global userID, isLoggedIn
        userID = 0
        isLoggedIn = True

        user = db.session.execute(select(us.fullname, us.id, us.is_logged_in, us.role).where(us.id == userID))
        user = user.first()
        # print(user)
        # print(user.role)
        db.session.execute(update(us)
                        .where(us.id == user.id)
                        .values(is_logged_in=True))
        # print(user.is_logged_in)
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
            eventArray.append({
                "event_id": event.id,
                "event_name": event.event_name,
                "date": event.date.strftime("%x"),
                "description": event.description,
                "organizer_id": event.organizer_id,
                "organizer_name": event.organizer_name
            })
        print(eventArray)
        return eventArray, user

    @a.route('/index2')
    def index2():
        events, user  = DBTest.db_join_test()
        print(events)
        return render_template('index2.html', user_id=userID, user=user, events=events, status=isLoggedIn)
        

import ipinfo, json, socket
class IPTest:

    def ipinfos():
        hostname = socket.gethostname()
        ipaddr = socket.gethostbyname(hostname)

        access_token = '2b1e26bf289858'
        handler = ipinfo.getHandler(access_token)
        details = handler.getDetails()

        return {
                "socket_ip": ipaddr,
                "ipinfo": details.all
            }

def write(file, info):
    with open(file, "w") as f:
        f.write(json.dumps(info, indent=4))


import arrow
class ArrowTest:
    now = arrow.utcnow()
    format = 'dddd, MMMM D, YYYY'
    formatted = now.format(format)

def run_tests():
    print(ArrowTest.formatted)
    # app = DBTest.make_app()
    app, URI = config.make_app(config.APP_CONFIG)
    return app


import unittest
from datastructure import User, Event, Volunteer1, Participant1, app, db

class TestUserModel(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_user(self):
        user = User(fname='John', lname='Doe', username=12345, email='john@example.com', role='default')
        db.session.add(user)
        db.session.commit()

        retrieved_user = User.query.filter_by(username=12345).first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.fname, 'John')
        self.assertEqual(retrieved_user.lname, 'Doe')
        self.assertEqual(retrieved_user.email, 'john@example.com')
        self.assertEqual(retrieved_user.role, 'default')

    def test_user_repr(self):
        user = User(fname='Jane', lname='Doe', username=54321, email='jane@example.com', role='admin')
        db.session.add(user)
        db.session.commit()

        self.assertEqual(repr(user), '<User "Jane Doe">')

if __name__ == '__main__':
    unittest.main()

class TestEventModel(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        db.create_all()
        user = User(fname='Organizer', lname='One', username=11111, email='organizer@example.com', role='organizer')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_event(self):
        organizer = User.query.filter_by(username=11111).first()
        event = Event(type='volunteer-only', event_name='Cleanup Drive', date='2024-07-20', organizer_id=organizer.id)
        db.session.add(event)
        db.session.commit()

        retrieved_event = Event.query.filter_by(event_name='Cleanup Drive').first()
        self.assertIsNotNone(retrieved_event)
        self.assertEqual(retrieved_event.type, 'volunteer-only')
        self.assertEqual(retrieved_event.date, '2024-07-20')
        self.assertEqual(retrieved_event.organizer_id, organizer.id)

    def test_event_repr(self):
        organizer = User.query.filter_by(username=11111).first()
        event = Event(type='volunteer-only', event_name='Beach Cleanup', date='2024-08-15', organizer_id=organizer.id)
        db.session.add(event)
        db.session.commit()

        self.assertEqual(repr(event), '<Event "Beach Cleanup...">')

if __name__ == '__main__':
    unittest.main()

class TestVolunteerModel(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        db.create_all()
        user = User(fname='Volunteer', lname='One', username=22222, email='volunteer@example.com', role='default')
        event = Event(type='volunteer-only', event_name='Park Cleanup', date='2024-07-10', organizer_id=1)
        db.session.add(user)
        db.session.add(event)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_volunteer(self):
        volunteer = User.query.filter_by(username=22222).first()
        event = Event.query.filter_by(event_name='Park Cleanup').first()
        volunteer_entry = Volunteer1(type='community-event', event_id=event.id, user_id=volunteer.id)
        db.session.add(volunteer_entry)
        db.session.commit()

        retrieved_volunteer = Volunteer1.query.filter_by(user_id=volunteer.id, event_id=event.id).first()
        self.assertIsNotNone(retrieved_volunteer)
        self.assertEqual(retrieved_volunteer.type, 'community-event')

    def test_volunteer_repr(self):
        volunteer = User.query.filter_by(username=22222).first()
        event = Event.query.filter_by(event_name='Park Cleanup').first()
        volunteer_entry = Volunteer1(type='community-event', event_id=event.id, user_id=volunteer.id)
        db.session.add(volunteer_entry)
        db.session.commit()

        self.assertEqual(repr(volunteer_entry), f'<Volunteer {volunteer.id} volunteered at Event {event.id}>')

if __name__ == '__main__':
    unittest.main()

class TestParticipantModel(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        db.create_all()
        user = User(fname='Participant', lname='One', username=33333, email='participant@example.com', role='default')
        event = Event(type='participate-only', event_name='Charity Run', date='2024-07-05', organizer_id=1)
        db.session.add(user)
        db.session.add(event)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_participant(self):
        participant = User.query.filter_by(username=33333).first()
        event = Event.query.filter_by(event_name='Charity Run').first()
        participant_entry = Participant1(event_id=event.id, user_id=participant.id)
        db.session.add(participant_entry)
        db.session.commit()

        retrieved_participant = Participant1.query.filter_by(user_id=participant.id, event_id=event.id).first()
        self.assertIsNotNone(retrieved_participant)

    def test_participant_repr(self):
        participant = User.query.filter_by(username=33333).first()
        event = Event.query.filter_by(event_name='Charity Run').first()
        participant_entry = Participant1(event_id=event.id, user_id=participant.id)
        db.session.add(participant_entry)
        db.session.commit()

        self.assertEqual(repr(participant_entry), f'<Participant {participant.id}.fname participated at Event {event.id}.">')

if __name__ == '__main__':
    unittest.main()

