from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "traveloop_secret_key_2024"

users = {}
trips = {}
trip_id_counter = 1

def get_user_trips(username):
    return [t for t in trips.values() if t["owner"] == username]

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username in users and users[username]["password"] == password:
            session["user"] = username
            flash(f"Welcome back, {username}! 🌍", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        email    = request.form.get("email", "").strip()
        if not username or not password:
            flash("Username and password are required.", "danger")
        elif username in users:
            flash("Username already taken.", "danger")
        else:
            users[username] = {
                "password": password,
                "email": email,
                "joined": datetime.now().strftime("%Y-%m-%d"),
                "avatar": username[0].upper()
            }
            session["user"] = username
            flash("Account created! Let's explore the world 🗺️", "success")
            return redirect(url_for("dashboard"))
    return render_template("login.html", register=True)

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You've been logged out. Safe travels! ✈️", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    user_trips = get_user_trips(session["user"])
    return render_template("dashboard.html", trips=user_trips, user=session["user"])


@app.route("/my_trips")
@login_required
def my_trips():
    user_trips = get_user_trips(session["user"])
    return render_template("my_trips.html", trips=user_trips)


@app.route("/create_trip", methods=["GET", "POST"])
@login_required
def create_trip():
    global trip_id_counter
    if request.method == "POST":
        trip = {
            "id": trip_id_counter,
            "owner": session["user"],
            "title": request.form.get("title", "Untitled Trip"),
            "destination": request.form.get("destination", ""),
            "start_date": request.form.get("start_date", ""),
            "end_date": request.form.get("end_date", ""),
            "budget": float(request.form.get("budget", 0) or 0),
            "notes": request.form.get("notes", ""),
            "activities": [],
            "packing_list": [],
            "expenses": [],
            "itinerary": [],
            "shared_with": [],
            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        trips[trip_id_counter] = trip
        trip_id_counter += 1
        flash(f"Trip to {trip['destination']} created! 🎉", "success")
        return redirect(url_for("itinerary_view", trip_id=trip["id"]))
    return render_template("create_trip.html")


@app.route("/trip/<int:trip_id>/itinerary", methods=["GET", "POST"])
@login_required
def itinerary_view(trip_id):
    trip = trips.get(trip_id)
    if not trip:
        flash("Trip not found.", "danger")
        return redirect(url_for("my_trips"))
    if request.method == "POST":
        day   = request.form.get("day", "Day 1")
        entry = request.form.get("entry", "").strip()
        time  = request.form.get("time", "")
        if entry:
            trip["itinerary"].append({"day": day, "entry": entry, "time": time})
            flash("Itinerary updated!", "success")
    return render_template("itnerary_view.html", trip=trip)


@app.route("/city_search")
@login_required
def city_search():
    query = request.args.get("q", "")
    return render_template("city_search.html", query=query)


@app.route("/trip/<int:trip_id>/activity", methods=["GET", "POST"])
@login_required
def activity(trip_id):
    trip = trips.get(trip_id)
    if not trip:
        flash("Trip not found.", "danger")
        return redirect(url_for("my_trips"))
    if request.method == "POST":
        act = {
            "name": request.form.get("name", ""),
            "date": request.form.get("date", ""),
            "cost": float(request.form.get("cost", 0) or 0),
            "notes": request.form.get("notes", "")
        }
        trip["activities"].append(act)
        flash("Activity added!", "success")
    return render_template("activity.html", trip=trip)


@app.route("/trip/<int:trip_id>/packing", methods=["GET", "POST"])
@login_required
def packing_checking(trip_id):
    trip = trips.get(trip_id)
    if not trip:
        flash("Trip not found.", "danger")
        return redirect(url_for("my_trips"))
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            item = request.form.get("item", "").strip()
            category = request.form.get("category", "General")
            if item:
                trip["packing_list"].append({"item": item, "category": category, "packed": False})
                flash("Item added to packing list!", "success")
        elif action == "toggle":
            idx = int(request.form.get("idx", -1))
            if 0 <= idx < len(trip["packing_list"]):
                trip["packing_list"][idx]["packed"] = not trip["packing_list"][idx]["packed"]
        elif action == "delete":
            idx = int(request.form.get("idx", -1))
            if 0 <= idx < len(trip["packing_list"]):
                trip["packing_list"].pop(idx)
    return render_template("packing_checking.html", trip=trip)


@app.route("/trip/<int:trip_id>/budget", methods=["GET", "POST"])
@login_required
def trip_budget(trip_id):
    trip = trips.get(trip_id)
    if not trip:
        flash("Trip not found.", "danger")
        return redirect(url_for("my_trips"))
    if request.method == "POST":
        expense = {
            "category": request.form.get("category", "Other"),
            "description": request.form.get("description", ""),
            "amount": float(request.form.get("amount", 0) or 0),
            "date": request.form.get("date", datetime.now().strftime("%Y-%m-%d"))
        }
        trip["expenses"].append(expense)
        flash("Expense recorded!", "success")
    total_spent = sum(e["amount"] for e in trip["expenses"])
    remaining   = trip["budget"] - total_spent
    return render_template("trip_budget.html", trip=trip, total_spent=total_spent, remaining=remaining)


@app.route("/trip/<int:trip_id>/notes", methods=["GET", "POST"])
@login_required
def trip_notes(trip_id):
    trip = trips.get(trip_id)
    if not trip:
        flash("Trip not found.", "danger")
        return redirect(url_for("my_trips"))
    if request.method == "POST":
        trip["notes"] = request.form.get("notes", "")
        flash("Notes saved!", "success")
    return render_template("trip_notes.html", trip=trip)


@app.route("/trip/<int:trip_id>/share", methods=["GET", "POST"])
@login_required
def shared_itinerary(trip_id):
    trip = trips.get(trip_id)
    if not trip:
        flash("Trip not found.", "danger")
        return redirect(url_for("my_trips"))
    if request.method == "POST":
        share_user = request.form.get("share_with", "").strip()
        if share_user and share_user not in trip["shared_with"]:
            trip["shared_with"].append(share_user)
            flash(f"Trip shared with {share_user}!", "success")
    return render_template("shared.itnerary.html", trip=trip)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def user_profile():
    user_data = users.get(session["user"], {})
    if request.method == "POST":
        users[session["user"]]["email"] = request.form.get("email", user_data.get("email", ""))
        flash("Profile updated!", "success")
    user_trips = get_user_trips(session["user"])
    return render_template("user_profile.html", user=session["user"], user_data=user_data, trips=user_trips)


if __name__ == "__main__":
    app.run(debug=True, port=5500)