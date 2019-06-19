from flask import Flask
from flask_restful import Api
from models.station_model import StationData, StationModel, OniData
import sqlite3
from db import db


uri = 'sqlite:///data.db'
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = uri
api = Api(app)
db.init_app(app)


@app.before_first_request
def create_tables():
    db.create_all()
    from datetime import datetime
    from siphon.simplewebservice.igra2 import IGRAUpperAir
    from models.station_model import StationData, StationModel, OniData

    beginning = [datetime(2013, 1, 11), datetime(2013, 6, 14)]
    station = 'USM00072250'

    df, header = IGRAUpperAir.request_data(beginning, station)

    x = 0
    station = StationModel(station, header['latitude'][0], header['longitude'][0])
    station.save_to_db()
    test = df.notnull()
    while x < len(df['height']):
        year = df['date'][x].strftime("%Y")
        month = df['date'][x].strftime("%m")
        oni = OniData.find_by_date(int(year), int(month))

        if test['temperature'][x] and test['height'][x]:
            station_data = StationData(df['date'][x],
                                       oni,
                                       int(df['height'][x]),
                                       df['temperature'][x],
                                       1)
            station_data.save_to_db()
        x += 1


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
