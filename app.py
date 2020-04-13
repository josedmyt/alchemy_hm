import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
session= Session(engine)

Measurement = Base.classes.measurement
Station =Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date(yyyy-mm-dd)<br/>"
        f"/api/v1.0/start_date/end_date(yyyy-mm-dd)<br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():

    session = Session(engine)
    precip = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    precip_final = []
    for date, prcp in precip:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip_final.append(precip_dict)
    return jsonify(precip_final)

@app.route('/api/v1.0/stations')
def stations():
    
    session = Session(engine)
    stations = session.query(Station.name).all()
    session.close()
    stations_final = list(np.ravel(stations))
    return jsonify(stations_final)

@app.route('/api/v1.0/tobs')
def tobs():

    session = Session(engine)
    active_stations = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >"2016-8-23").\
        filter(Measurement.station =="USC00519281").all()
    session.close()
    temps = []
    for entry in active_stations:
        row = {}
        row["date"] = entry[0]
        row["temperature"] = entry[1]
        temps.append(row)
    return jsonify(temps)

@app.route('/api/v1.0/<start_date>')
def start(start_date):
    session=Session(engine)
    dates = session.query(Measurement.tobs).\
        filter(Measurement.date >= start_date).\
        order_by(Measurement.tobs).all()
    session.close()

    row = {}
    row['Date'] = start_date
    row['TMIN'] = int(dates[0][0])
    row['TAVG'] = int(np.mean(dates))
    row['TMAX'] = dates[-1][0]
    return jsonify(row)

@app.route('/api/v1.0/<start_date>/<end_date>')
def start_end(start_date, end_date):
    session=Session(engine)
    dates2 = session.query(Measurement.tobs) .\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).\
        order_by(Measurement.tobs).all()
    session.close()
    
    row = {}
    row['Date Range'] = start_date + ":" + end_date
    row['TMIN'] = int(dates2[0][0])
    row['TAVG'] = int(np.mean(dates2))
    row['TMAX'] = dates2[-1][0]
    return jsonify(row)

if __name__ == '__main__':
    app.run(debug=True)

