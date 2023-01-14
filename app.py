import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from datetime import datetime
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

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
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE Username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hashed_pwd"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["ID"]

        # Redirect user to home page
        return redirect("/userhome")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login1.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/shop")
@login_required
def shop():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif request.form.get("confirm_password") != request.form.get("password"):
            return apology("passwords don't match", 400)

        username = request.form.get("username")

        hashed_password = generate_password_hash(request.form.get("password"))

        try:
            registrant = db.execute(
                "INSERT INTO users (username, hashed_pwd) VALUES (?, ?)",
                username,
                hashed_password,
            )
            db.execute("CREATE TABLE ? (PetID INTEGER PRIMARY KEY, Petname TEXT, Petkind TEXT, Age INTEGER, Weight INTEGER, Vaccinated BOOLEAN)", username)
        except:
            return apology("Username exists", 400)

        session["user_id"] = registrant

        flash("Registered!")
        return redirect("/userhome")

    else:
        # Render page if requested via GET
        return render_template("register1.html")


@app.route("/userhome")
@login_required
def userhome():    
    username = db.execute("SELECT Username FROM users WHERE ID = ?", session["user_id"])
    petdetails = db.execute("SELECT * FROM ?", username[0]['Username'])
    print(petdetails)
    return render_template("userhome.html", petdetails=petdetails)


@app.route("/addpet", methods=['GET', 'POST'])
@login_required
def addpet():
    if request.method=="POST":
        petname = request.form.get("petname")
        petkind = request.form.get("petkind")
        age = request.form.get("age")
        weight = request.form.get("weight")
        vaccinated = request.form.get("vaccinated")
        print(vaccinated)

        username = db.execute("SELECT Username FROM users WHERE ID = ?", session["user_id"])
        
        db.execute("INSERT INTO ? (Petname, Petkind, Age, Weight, Vaccinated) VALUES (?, ?, ?, ?, ?)", username[0]['Username'], petname, petkind, age, weight, vaccinated)

        return redirect("/userhome")
    else:
        return render_template("addpet.html")


@app.route("/report", methods=["GET","POST"])
def report():
    if request.method=="GET":
        return render_template("report1.html")
    else:
        state = request.form.get("state")
        city = request.form.get("city")
        animal_type = request.form.get("animal_type")
    
    import math
    hospitals = db.execute("SELECT * FROM HospitalInfo WHERE Type = ?", animal_type)
    print("Hospitals", hospitals)
    # Import the required library
    from geopy.geocoders import Nominatim

    # Initialize Nominatim API
    geolocator = Nominatim(user_agent="MyApp")

    location = geolocator.geocode(city)

    print("The latitude of the location is: ", location.latitude)
    print("The longitude of the location is: ", location.longitude)

    lat1 = location.latitude
    long1 = location.longitude
    def distance_on_unit_sphere(lat1, long1, lat2, long2):

        # Converts lat & long to spherical coordinates in radians.
        degrees_to_radians = math.pi/180.0

        # phi = 90 - latitude
        phi1 = (90.0 - lat1)*degrees_to_radians
        phi2 = (90.0 - lat2)*degrees_to_radians

        # theta = longitude
        theta1 = long1*degrees_to_radians
        theta2 = long2*degrees_to_radians

        # Compute the spherical distance from spherical coordinates.

        cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
        math.cos(phi1)*math.cos(phi2))
        arc = math.acos(cos)*6371 #radius of the earth in km

        return arc

    distance_list=[]
    for hospital in hospitals:
        name, latitude, longitude = hospital['Name'], hospital['Latitude'], hospital['Longitude']
        latitude = float(latitude)
        longitude = float(longitude)
        distance_list.append([distance_on_unit_sphere(latitude, longitude, lat1, long1),latitude,longitude])

    distance_list.sort()
    print(distance_list)

    finalhospinfo = []
    count=0
    for i in distance_list:
        for j in hospitals:
            lattrue=False
            longtrue=False
            lati=float(i[1])
            longi=float(i[2])
            for key, value in j.items():
                if((type(value)==float and key=='Latitude') or type(value)==float and key=='Longitude'):
                    if(value==lati):
                        lattrue=True
                    if(value==longi):
                        longtrue=True
            if(lattrue==True and longtrue==True):
                finalhospinfo.append(j)
            #print(j)
            
            #if(j['Latitude']==lati and j['Longitude']==longi):
             #   finalhospinfo.append(j)
        '''
        if(count<20):
            lat=i[1]
            long=i[2]
            print(lat, long)
            hospinfo = db.execute("SELECT * FROM HospitalInfo WHERE Latitude=? AND Longitude=?", lat, long)
            print(hospinfo)
            finalhospinfo.append(hospinfo)
            count += 1
        else:
            break
        '''
        
    print('The final list is', finalhospinfo)
    return render_template("hosplist.html", hosp=finalhospinfo)


@app.route("/health/", methods=["GET", "POST"])
@login_required
def healthcard():
    if request.method=="POST":
        name_of_pet = request.form.get("name_of_pet")
        username = db.execute("SELECT Username FROM users WHERE ID = ?", session["user_id"])
        pets = db.execute("SELECT * FROM ? WHERE Petname=?", username[0]['Username'], name_of_pet)
        return redirect('/health')
    else:
        username = db.execute("SELECT Username FROM users WHERE ID = ?", session["user_id"])
        petnames = db.execute("SELECT Petname FROM ?", username[0]['Username'])
        return render_template("health.html", petnames=petnames)
        


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


#TESTING NEAREST LOCATIONS--------------------------------------------------------------------------------



