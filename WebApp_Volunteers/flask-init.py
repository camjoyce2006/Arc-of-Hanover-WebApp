from flask import Flask, render_template
from markupsafe import escape

app = Flask(__name__)

#Static route 1
@app.route('/home')
def home():
    return (
        '<h1>Home page</h1>'
    )

#Dynamic route
@app.route('/home/<name>')
def homeName(name):
    hi = "Home"
    return (
        '<head><title>{}\'s Home Page</title></head>'.format(name)+
        '<h1>Welcome, {}!</h1>'.format(escape(name))
    )
#Static route 2
@app.route('/bible')
def quoteStorage():
    title="Bible Verses"
    return (
        render_template('flask-test.html', tabname=title)
    )

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)