import math
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from geopy.geocoders import Nominatim
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

#from helpers import apology, login_required

# Configure application
app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///vet.db")
geolocator = Nominatim(user_agent="MyApp")
HOSP_PASS = generate_password_hash("#a1b2z26y25@!")


def distance(lat1, long1, lat2, long2):

    R = 6371 # Radius of the earth in km

    Latdiff = math.radians(lat2-lat1)
    Longdiff = math.radians(long2-long1)
    calc1 = math.sin(Latdiff/2) * math.sin(Latdiff/2) + math.cos(math.radians(lat1))* math.cos(math.radians(lat2)) * math.sin(Longdiff/2) * math.sin(Longdiff/2)
    distance = R * 2 * math.atan2(math.sqrt(calc1), math.sqrt(1-calc1)) 
    return distance


def get_coords(locality, city, state):
    location = geolocator.geocode(f"{locality}, {city}, {state}")

    lat1 = location.latitude    #user latitude
    long1 = location.longitude  #user longitude
    
    return lat1, long1


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/", methods=["GET", "POST"])
def homepage():
    """show home page with 3 buttons register, login, complaint"""
    return render_template("home.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE Username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hashed_pwd"], request.form.get("password") # type: ignore
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["ID"]

        # Redirect user to home page
        return redirect("/userhome")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login1.html")


@app.route('/resetpass', methods=["GET", "POST"])
def resetpass():
    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("newpass") or not request.form.get("retypenewpass") or not request.form.get("email") or not request.form.get("contact"):
            return apology("Must fill all fields")
        
        if request.form.get("newpass") != request.form.get("retypenewpass"):
            return apology("Passwords don't match")
        
        username = request.form.get("username")
        email = request.form.get("email")
        contact = request.form.get("contact")
        hashed_newpass = generate_password_hash(request.form.get("newpass"))
        
        if not db.execute("SELECT * FROM users WHERE Username = ? AND Email = ? AND Contact = ?", username, email, contact):
            return apology("Invalid details. Try again")
        
        updated = db.execute("UPDATE users SET (hashed_pwd) = ? WHERE (Username) = ?", hashed_newpass, username)
        
        if not updated:
            return apology("Invalid details. Register again")
        
        return redirect('/login')
    
    return render_template("resetpass.html")
    

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 400)
        
        if not request.form.get("email"):
            return apology("must provide email ID", 400)
        
        if not request.form.get("contact"):
            return apology("must provide Contact number", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)

        if request.form.get("confirm_password") != request.form.get("password"):
            return apology("passwords don't match", 400)

        username = request.form.get("username")
        email = request.form.get("email")
        contact = request.form.get("contact")

        hashed_password = generate_password_hash(request.form.get("password")) # type: ignore

        try:
            registrant = db.execute(
                "INSERT INTO users (username, hashed_pwd, Contact, Email) VALUES (?, ?, ?, ?)",
                username,
                hashed_password,
                contact,
                email
            )
            db.execute("CREATE TABLE ? (PetID INTEGER PRIMARY KEY, Petname TEXT, Petkind TEXT, Age INTEGER, Weight INTEGER, Vaccinated BOOLEAN, Notes TEXT)", username)
        except :
            return apology("Username exists", 400)

        session["user_id"] = registrant

        flash("Registered!")
        return redirect("/userhome")

    # Render page if requested via GET
    return render_template("register1.html")


@app.route("/userhome")
@login_required
def userhome():    
    username = db.execute("SELECT Username FROM users WHERE ID = ?", session["user_id"])
    petdetails = db.execute("SELECT * FROM ?", username[0]['Username'])
    counter = 1
    for pet in petdetails:
        pet['PetID'] = counter
        counter += 1
    
    return render_template("userhome.html", petdetails=petdetails)


@app.route("/addpet", methods=['GET', 'POST'])
@login_required
def addpet():
    if request.method=="POST":
        
        if not request.form.get("petname"):
            return apology("Must provide pet name.")
        
        if not request.form.get("petkind") or request.form.get("petkind") == "Pet kind":
            return apology("Must provide type of pet.")
        
        petname = request.form.get("petname")
        petkind = request.form.get("petkind")
        age = request.form.get("age")
        weight = request.form.get("weight")
        vaccinated = request.form.get("vaccinated")
        notes = request.form.get("notes")
        print(notes)

        username = db.execute("SELECT Username FROM users WHERE ID = ?", session["user_id"])
        
        db.execute("INSERT INTO ? (Petname, Petkind, Age, Weight, Vaccinated, Notes) VALUES (?, ?, ?, ?, ?, ?)", username[0]['Username'], petname, petkind, age, weight, vaccinated, notes)

        return redirect("/userhome")
    
    return render_template("addpet.html")

@app.route("/deletepet", methods=["GET", "POST"])
@login_required
def deletepet():
    if request.method == "POST":
        if not request.form.get("petname"):
            return apology("Must provide name of pet to remove")

        petname = request.form.get("petname")
        username = db.execute("SELECT Username FROM users WHERE ID = ?", session["user_id"])
        
        try:
            db.execute("DELETE FROM ? WHERE (Petname) = (?)", username[0]['Username'], petname)
        except:
            return apology(f"Pet {petname} not found")
        
        return redirect('/userhome')
                
    return render_template("deletepet.html")

@app.route("/updatepet", methods=["GET", "POST"])
@login_required
def updatepet():
    if request.method == "POST":
        if not request.form.get("oldpetname"):
            return apology("Must provide name of pet")
        
        username = db.execute("SELECT Username FROM users WHERE ID = ?", session["user_id"])
        
        oldname = request.form.get("oldpetname")
        newname = request.form.get("newpetname")
        petkind = request.form.get("petkind")
        age = request.form.get("age")
        weight = request.form.get("weight")
        vaccinated = request.form.get("vaccinated")
        notes = request.form.get("notes")
        
        storedpets = [item['Petname'] for item in db.execute("SELECT (Petname) FROM ?", username[0]["Username"])]
        if oldname not in storedpets:
            return apology(f"Pet {oldname} not found")
        
        try:
            if petkind:
                db.execute("UPDATE ? SET (Petkind) = ? WHERE (Petname) = ?", username[0]['Username'], petkind, oldname)
            
            if age:
                db.execute("UPDATE ? SET (Age) = ? WHERE (Petname) = ?", username[0]['Username'], age, oldname)
                
            if weight:
                db.execute("UPDATE ? SET (Weight) = ? WHERE (Petname) = ?", username[0]['Username'], weight, oldname)
                
            if notes:
                db.execute("UPDATE ? SET (Notes) = ? WHERE (Petname) = ?", username[0]['Username'], notes, oldname)
                
                
            db.execute("UPDATE ? SET (Vaccinated) = ? WHERE (Petname) = ?", username[0]["Username"], vaccinated, oldname)
            
            if newname:
                db.execute("UPDATE ? SET (Petname) = ? WHERE (Petname) = ?", username[0]['Username'], newname, oldname)
            
        except:
            return apology(f"Pet '{oldname}' not found")
        
        return redirect("/userhome")
    
    return render_template("updatepet.html")
            

@app.route("/report", methods=["GET","POST"])
def report():
    if request.method=="GET":
        return render_template("report1.html")
    else:
        if not request.form.get("locality"):
            return apology("Must provide locality")
        
        if not request.form.get("state"):
            return apology("Must provide state.")
        
        if not request.form.get("city"):
            return apology("Must provide city")
        
        if not request.form.get("animal_type"):
            return apology("Must specify animal type")
        
        locality = request.form.get("locality")
        state = request.form.get("state")
        city = request.form.get("city")
        animal_type = request.form.get("animal_type")

        lat1, long1 = get_coords(locality, city, state)
        
        if not lat1 or not long1:
            return apology("Your location not found")

        hospitals = db.execute("SELECT * FROM HospitalInfo WHERE Type = ? OR Type = 'All'", animal_type)
    
        distances = []

        for hospital in hospitals:
            lat2 = hospital['Latitude']
            long2 = hospital['Longitude']
            
            dist = distance(lat1, long1, lat2, long2)
            
            distances.append({hospital['Name']:dist})
        
        for i in range(len(hospitals)):
            hospitals[i]['Distance'] = distances[i][hospitals[i]['Name']]
            
        hospitals = sorted(hospitals, key=lambda x: x['Distance'])[:4]
        
        return render_template("hosplist.html", hosp = hospitals)


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


@app.route("/addhosp", methods=['GET', 'POST'])
def addhosp():
    if request.method == 'POST':
        
        if not request.form.get("auth_id") or not request.form.get("hosp_name") or not request.form.get("type") or not request.form.get("location") or not request.form.get("latitude") or not request.form.get("longitude") or not request.form.get("contact"):
            return apology("Fill all fields")
        
        auth_id = request.form.get("auth_id")
        hosp_name = request.form.get("hosp_name")
        type = request.form.get("type")
        location = request.form.get("location")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        contact = request.form.get("contact")
        weblink = request.form.get("weblink")
        

        map_link = f"https://google.com/maps/place/{latitude}+{longitude}"
        
        if (check_password_hash(HOSP_PASS, auth_id) == True):
            # Add details to db
            db.execute("INSERT INTO HospitalInfo (Name, Type, Address, Latitude, Longitude, Contact_details, Map_link, Web_link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", hosp_name, type, location, latitude, longitude, contact, map_link, weblink)
        else:
            return apology("Invalid Authentication ID")
        
        return redirect('/')
    
    return render_template("addhosp.html")
        