# Import the dependencies.

from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import func
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

app = Flask(__name__)

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Routes
#################################################

@app.route('/')
def home():
    return (
        f"Welcome to my Climate App<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year ago from the last date in the dataset
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = (dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)).date()
    
    # Query to get precipitation data for the last 12 months
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a dictionary
    prcp_dict = {date: prcp for date, prcp in prcp_data}
    
    return jsonify(prcp_dict)

@app.route('/api/v1.0/stations')
def stations():
    # Query all station names
    station_names = session.query(Station.station).all()
    station_list = list(np.ravel(station_names))  # Convert to a flat list
    
    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    # Calculate the date one year ago from the last date in the dataset
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = (dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)).date()
    
    # Query temperature observations for the most active station for the last 12 months
    most_active_station_id = "USC00519281"  # Replace with the actual most active station id
    temp_data = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == most_active_station_id, Measurement.date >= one_year_ago).all()
    
    temp_list = [{"date": date, "temperature": tobs} for date, tobs in temp_data]
    
    return jsonify(temp_list)

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def temp_summary(start, end=None):
    if not end:
        end = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    
    # Query to calculate TMIN, TAVG, and TMAX for the specified date range
    temp_summary_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date.between(start, end)).all()
    
    temp_summary = {
        "start_date": start,
        "end_date": end,
        "TMIN": temp_summary_data[0][0],
        "TAVG": temp_summary_data[0][1],
        "TMAX": temp_summary_data[0][2]
    }
    
    return jsonify(temp_summary)

if __name__ == '__main__':
    app.run(debug=True)

