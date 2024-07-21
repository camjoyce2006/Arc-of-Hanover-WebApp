from datastructure import User, db
import logging, socket
from flask import session
from datetime import timezone, datetime

# Method that dynamically updates attributes of a database row
def update_db(model, row:object, values:dict[str, str], add=False, **kwargs):

    def findValidID(model=model):
        id = 1
        ids = [row.id for row in model.query.all()]
        while id in ids:
            id += 1
        return id
    
    colkeys = model.__table__.columns.keys()
    values = {k: v for k, v in values.items()}
    values.update(kwargs)
    valid_cols = [colkey for colkey in colkeys if colkey in values.keys()]
    for col in valid_cols:
        current_value = row.__getattribute__(col)
        new_value = values[col]
        if current_value != new_value:
            if new_value == 'y':
                new_value = True
            elif new_value == 'n':
                new_value = False
            row.__setattr__(col, new_value)
            
            if type(new_value) is str:
                new_value = new_value[:20]
            
            if not add:
                print(f"{model.__qualname__} {row.id} attribute '{col}' was updated to '{new_value}...'")
    
    if add:
        row.id = findValidID()
        db.session.add(row)
    db.session.commit()


# Method to update session info when a user logs in or out
def update_session(action:str, user_id:int = 8, endpoint = None):
    user = User.query.filter_by(id=user_id).first()
    if action == 'login':
        act = True
    elif action == 'signout':
        act = False
    elif action == 'first':
        act = False
        session['initialization_done'] = True
        session['current_page'] = endpoint
        session['previous_page'] = None
        print('Initialization complete.')
    elif action == 'page':
        if endpoint and endpoint != session.get('current_page'):
            session['previous_page'] = session.get('current_page')
        session['current_page'] = endpoint
        act = session.get('is_logged_in')
    if user:
        session['user_id'] = user_id
        session['username'] = user.fullname
        if act != session.get('is_logged_in'):
            user.is_logged_in = act
            db.session.commit()
            session['is_logged_in'] = user.is_logged_in
    return get_session_info(None)

# Method that gets session variables
def get_session_info(var: str | None = None):
    info = session.get(var)
    if info:
        return info
    if var == 'user':
        return User.query.filter_by(id=session.get('user_id')).first()
    return {
        "user_id": session.get('user_id'),
        "user": User.query.filter_by(id=session.get('user_id')).first(),
        "username": session.get('username'),
        "is_logged_in": session.get('is_logged_in'),
        "current_page": session.get('current_page'),
        "previous_page": session.get('previous_page')
    }
        
#Method that writes all server events to an audit file.
def logEvents(type:str, level:str, message:str):
    logger = logging.getLogger(__name__)
    timeNow = datetime.now(timezone.utc).strftime("%d/%b/%Y %H:%M:%S")
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    message = f'{IPAddr} - [{timeNow}]: {message}'

    def getAuditFile(type):
        if type == 'login':
            return ['audit_all.log', 'audit_login.log']
        return ['audit_all.log']

    for file in getAuditFile(type):
        logging.basicConfig(filename=file, level=logging.DEBUG)
        if level =='d':
            logger.debug(message)
        elif level == 'w':
            logger.warning(message)
        elif level == 'e':
            logger.error(message)
        elif level == 'i':
            logger.info(message)
        logger.info(message)
    print(message)
