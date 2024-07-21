from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import os

CONFIG_MODE = 'dev'

#Set environment variables
env_vars = load_dotenv(dotenv_path="env_vars.env", override=True)
ENV_LIST = ['DB', 'DB_UN', 'DB_PW']

def check_envs(
        env_dict: list[str] = ENV_LIST
        ) -> bool | None:
    for key in env_dict:
        if key not in os.environ:
            raise ValueError(f"Environment variable \'{key}\' not set.")
    return True

URI = None
if check_envs():
    URI = 'postgresql://'+\
            os.environ['DB_UN']+':'+\
            os.environ['DB_PW']+\
            '@localhost:5432/'+\
            os.environ['DB']

#App configuration dictionary
APP_CONFIG =    {
    'SQLALCHEMY_DATABASE_URI': URI,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SECRET_KEY': '23ed506a97fd81899aa1a73a5354095972a6927ff50908e8'
}

# Port config
TEST_PORT = '5000'
DEV_PORT = '4000'

# Constants
USER_ROLES = [
        ('admin', 'Admin'),
        ('default', 'Default user'),
        ('organizer', 'Organizer'),
        ('store-manager', 'Thrift Store Manager') 
    ]



EVENT_TYPES = [
        ('volunteer-only', 'Volunteer-only'),
        ('participate-only', 'Participate-only'), 
        ('volunteer-participate', 'Volunteer or participate')
    ]

VOLUNTEER_TYPES = [
        ('community', 'Community Event'),
        ('thrift', 'Thrift Store'),
        ('none', 'No Volunteers')
    ]

STORE_DEPTS = [
        ('cashier', 'Cashier'),
        ('greeter', 'Greeter'),
        ('sorter',' Donation Sorting')
    ] # Need list from Sherri

STORE_SHIFTS = [
        ('Thursday', ['9:45-2:00', '2:00-6:15']),
        ('Friday', ['9:45-2:00', '2:00-6:15']),
        ('Saturday', ['9:45-1:30', '1:30-5:15'])
    ]

GENDERS = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('non-binary', 'Non-binary'),
        ('nosay', 'Prefer not to say')
    ]


class FlaskAppDB:
    """Creates a `Flask` app instance with a `SQLAlchemy` database session.
    """
    def __init__(
                self, 
                 name: str, 
                 uri: str | None = URI, 
                 flask_app: Flask | None = None, 
                 database: SQLAlchemy | None = None,
                 app_context = None
                 ) -> None:
        self.name = f"{name}-{CONFIG_MODE}"
        self.app = flask_app
        self.database =  database
        self.uri = uri
        self.app_context = None
        self.config = None
        self.is_configured = False
        self.app_context = app_context
        self.has_context = False
        self.make_app()
    
    # App configuration method
    def configure_app(
            self,
            config_dict: dict[str, any]
            ) -> None:
        for variable, value in config_dict.items():
            self.app.config[variable] = value
        
        self.uri = config_dict['SQLALCHEMY_DATABASE_URI']
        self.config = config_dict
        self.is_configured = True
        print('App configured.')

    # Set context
    def set_app_context(self) -> None:
        app_context = self.app.app_context()
        app_context.push()
        self.app_context = app_context
        self.has_context = True
        print('App context set.')

    # App creation method
    def make_app(
            self, 
            CONFIG_DICT: dict[str, any]=APP_CONFIG
        ) -> None:
    
        # Set environment variables
        if check_envs():

            # Create a Flask app
            self.app = Flask(__name__)
            
            # Set app.config variables
            self.configure_app(CONFIG_DICT)
            
            self.database = SQLAlchemy(self.app)

            if self.uri is not None:
                print (f"Connected to database at URI '{self.uri}'")
                return
            else:
                raise ValueError("'SQLALCHEMY_DATABASE_URI' must be set in order to connect to a database")
            
    def init_db(self, schema=None, create=True,  drop=True, insert=False, **kwargs):
        
        if not self.has_context:
            self.set_app_context()
        
        if schema:
            with self.app_context:
                self.database.session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
                return schema
        
        if create:
            if drop:
                self.database.drop_all()
                print('Dropped all tables')
            self.database.create_all()
            print('Successfully created tables')
        
        if insert:
            for key, value in kwargs.items():
                self.database.session.add_all(value)
                self.database.session.commit()
                print(f"Successfully added {key} to database")
