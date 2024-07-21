from datastructure import app, db
from sqlalchemy.ext.automap import automap_base
from flask import Flask, render_template
import json
from datetime import datetime, date
app2 = app

Base = automap_base()
Base.prepare(autoload_with=db.engine)

auto_tables = Base.classes.items()
def get_all_data(filename, write=False):
    storage = {}
    for name, model in auto_tables:
        print(f'------{name.title()}------')
        tableName = name
        model_rows = db.session.query(model).order_by(model.id.asc()).all()
        colkeys = model.__table__.columns.keys()
        caps = [colkey.split('_') for colkey in colkeys]
        real = [" ".join(colkey) for colkey in caps]
        storage.update({tableName: {
            "tablename": tableName,
            "row_count": db.session.query(model).count(),
            "col_keys": real,
            "rows": {}
            }})
        
        rows = storage[tableName]['rows']
        for row in model_rows:
            rows.update({row.id: {}})
            json_row = rows[row.id]
            
            for key in colkeys:
                value = row.__getattribute__(key)
                if type(value) is date:
                    value = value.strftime("%#m/%#d/%Y")
                if type(value) is datetime:
                    value = value.strftime("%#m/%#d/%Y %H:%M:%S")
                    
                json_row.update({key: value})

        print(f"Rows: {storage[tableName]['row_count']}")

    if write:      
        with open(filename, "w") as file:
            file.write(json.dumps(storage, indent=4))
    
    return storage

@app2.route('/')
def index():
    storage = get_all_data("data-save-7.9.2024.json", write=True)
    return render_template('dumps.html', json_object=storage)

@app2.route('/details')
def details():
    return render_template('dumps.html', json_object=None)

if __name__ == '__main__':
    app2.run(debug=True)