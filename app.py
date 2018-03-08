from flask import Flask, render_template, url_for, redirect, request, session, json, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

engine = create_engine("mysql://root:password@localhost/flask")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
        # """SHOW THE FORM AND DISPLAY THE AVILABLE FLIGHTS"""

    flights = db.execute("SELECT * FROM flights").fetchall()
    return(render_template("index.html", flights=flights))


@app.route("/Book", methods=["POST"])
def book():
        # """INSERT PASSENGERS TO THE DATABASE """

    name = request.form.get("name")
    try:
            # the flight_id is the value from the options,it's an id in the database
        flight_id = int(request.form.get("flight_id"))
    except ValueError:
        return(render_template("error.html", message="invalid flight number"))

    if db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).rowcount == 0:
        return(render_template("error.html", message="No such flight with that id"))

    db.execute("INSERT INTO passengers(name, flight) VALUES(:name, :flight)",
               {"name": name, "flight": flight_id})

    db.commit()
    return (render_template("success.html", name=name))


@app.route("/flights/<int:flight_id>")
def flights(flight_id):
        # """SHOW DETIALS ABOUT THE FLIGHT THAT HAVE THE arg flight_id"""
    flight = db.execute("SELECT * FROM flights WHERE id = :flight_id",
                        {"flight_id": flight_id}).fetchone()
    if flight is None:
        return(render_template("error.html", message="No such flight exist"))

    passengers = db.execute("SELECT * FROM passengers WHERE flight = :flight_id",
                            {"flight_id": flight_id})
    return(render_template("flights.html", flight=flight, passengers=passengers))


@app.route("/api/flights/<int:flight_id>")
def api(flight_id):
	# get all flights & check flight exist
	flight = db.execute("SELECT * FROM flights WHERE id = :flight_id",
                        {"flight_id": flight_id}).fetchall()

	if flight is None: return(jsonify({"error": "Invalid flight id, No such flight exist"}))

    passengers = db.execute("SELECT * FROM passengers WHERE flight = :flight_id",
	 						{"flight_id": flight_id})

	names = []
	for passenger in passengers:
		names.append(passenger.name)

    return({
			"origin": flight.origin,
			"destination": flight.destination,
			"duration": flight.duration,
			"passengers": names
		})


if __name__ == "__main__":
    app.run(debug=True)
