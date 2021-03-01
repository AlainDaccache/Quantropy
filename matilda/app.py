"""
You can run the flask app in terminal with the commands 'set FLASK_APP=matilda', then 'py -m flask run'
When it says 'Running on http://0.0.0.0:5000/', it means it is accepting connections on any network adapter,
not a specific one. Use 127.0.0.1 i.e. 'http://localhost:5000/' to actually connect to a server running on your machine.
"""

from . import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
