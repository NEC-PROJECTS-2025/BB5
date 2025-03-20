from flask import Flask, request, render_template, redirect, url_for, session
from flask_cors import cross_origin
import pickle
import pandas as pd

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session handling
model = pickle.load(open("flight_rf.pkl", "rb"))

@app.route("/")
@cross_origin()
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/project-info")
def project_info():
    return render_template("project_info.html")

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Hardcoded credentials (replace with database authentication)
        if username == "admin" and password == "password":
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

# Signup Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Save credentials in DB (not implemented here)
        return redirect(url_for("login"))
    
    return render_template("signup.html")

# Dashboard Route (for logged-in users)
@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    return redirect(url_for("login"))

# Logout Route
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

# Flight Price Prediction Route
@app.route("/predict", methods=["GET", "POST"])
@cross_origin()
def predict():
    if request.method == "POST":
        date_dep = request.form["Dep_Time"]
        Journey_day = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").day)
        Journey_month = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").month)

        Dep_hour = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").hour)
        Dep_min = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").minute)

        date_arr = request.form["Arrival_Time"]
        Arrival_hour = int(pd.to_datetime(date_arr, format="%Y-%m-%dT%H:%M").hour)
        Arrival_min = int(pd.to_datetime(date_arr, format="%Y-%m-%dT%H:%M").minute)

        dur_hour = abs(Arrival_hour - Dep_hour)
        dur_min = abs(Arrival_min - Dep_min)

        Total_stops = int(request.form["stops"])

        airline = request.form['airline']
        airlines = ['Jet Airways', 'IndiGo', 'Air India', 'Multiple carriers', 'SpiceJet',
                    'Vistara', 'GoAir', 'Multiple carriers Premium economy', 
                    'Jet Airways Business', 'Vistara Premium economy', 'Trujet']
        airline_features = [1 if airline == a else 0 for a in airlines]

        Source = request.form["Source"]
        sources = ['Delhi', 'Kolkata', 'Mumbai', 'Chennai']
        source_features = [1 if Source == s else 0 for s in sources]

        Destination = request.form["Destination"]
        destinations = ['Cochin', 'Delhi', 'New Delhi', 'Hyderabad', 'Kolkata']
        destination_features = [1 if Destination == d else 0 for d in destinations]

        prediction = model.predict([[Total_stops, Journey_day, Journey_month, Dep_hour, Dep_min,
                                     Arrival_hour, Arrival_min, dur_hour, dur_min, 
                                     *airline_features, *source_features, *destination_features]])

        output = round(prediction[0], 2)
        return render_template('home.html', prediction_text=f"Your Flight price is Rs. {output}")

    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
