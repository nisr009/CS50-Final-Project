import os
import re
from cs50 import SQL
from flask import Flask, redirect, render_template, session, request, flash, url_for, send_from_directory
from helpers import apology, login_required
from tempfile import mkdtemp
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session )
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.db")


@app.route("/")
def index():
    return render_template("website/home.html")


######################################################################################
##
##                         APP ADMIN  Section
##
######################################################################################

@app.route("/admin")
@login_required
def admin():
    return render_template("admin/admin.html")

@app.route("/users")
@login_required
def users():
    rows = db.execute("SELECT * FROM users")
    return render_template("admin/users.html", users = rows)

@app.route("/messages")
@login_required
def messages():
    rows=db.execute("SELECT * FROM messages")
    return render_template("admin/messages.html", messages=rows)

@app.route("/delmessage", methods=["GET", "POST"])
@login_required
def delmessage():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM messages")
        return render_template("admin/sites.html", messages=rows)
    elif request.method == "POST":
        if request.form["messageid"]:
            db.execute("DELETE FROM messages WHERE messageid = :messageid", messageid=request.form.get("messageid"))
        # Display a flash message
        flash("Message deleted !")
        return redirect("/messages")

####################   /BLOG    ##############################
@app.route("/articles")
@login_required
def articles():
    rows=db.execute("SELECT * FROM articles ORDER BY time DESC")
    return render_template("admin/postblog.html", articles=rows)

@app.route("/addblog", methods=["GET", "POST"])
@login_required
def addblog():
    if request.method == "GET":
        rows=db.execute("SELECT * FROM articles")
        return render_template("admin/addblog.html", articles=rows)
    elif request.method == "POST":
        db.execute("INSERT INTO articles (image, title, category, content, dateCreated, time) VALUES(:image, :title, :category, :content, :dateCreated, :time)",
                   image=request.form.get("image"), title=request.form.get("title"), category=request.form.get("category"),
                   content=request.form.get("content"), dateCreated=datetime.now(), time=datetime.now().time())
        # Display a flash message
        flash("Blog posted !")
    return redirect("/articles")

@app.route("/delblog", methods=["GET", "POST"])
def delblog():
    if request.method == "GET":
        return render_template("admin/admin.html")
    elif request.method == "POST":
        if request.form["articleid"]:
            db.execute("DELETE FROM articles WHERE articleid = :articleid", articleid=request.form.get("articleid"))
            # Display a flash message
            flash("Blog deleted !")
        return redirect("/articles")
####################   ./ BLOG    ############################


######################################################################################
##
##                         COMPANY ADMIN Section
##
######################################################################################

####################   /CALENDAR    ##############################
@app.route("/calendar")
@login_required
def calendar():
    rows=db.execute("SELECT * FROM employees")
    rows1=db.execute("SELECT * FROM clients")
    rows2=db.execute("SELECT * FROM sites")
    rows3=db.execute("SELECT * FROM vehicules")
    now = datetime.now()
    return render_template("admin/calendar.html", now=now,
            employees=rows,
            clients=rows1,
            sites=rows2,
            vehicules=rows3)




####################   ./ CALENDAR    ############################




####################   /EMPLOYEES    ############################
@app.route("/employees")
@login_required
def employees():
    rows = db.execute("SELECT * FROM employees")
    return render_template("admin/employees.html", employees=rows)

@app.route("/addemployee", methods=["GET", "POST"])
@login_required
def addemployee():
    if request.method == "GET":
        return render_template("admin/employees.html")
    elif request.method == "POST":
        if not request.form.get("name") or not request.form.get("lastname"):
            return render_template("apology.html")
        db.execute("INSERT INTO employees (name, lastname, email, phone, position) VALUES(:name, :lastname, :email, :phone, :position)",
                   name=request.form.get("name"), lastname=request.form.get("lastname"),
                   email=request.form.get("email"), phone=request.form.get("phone"),
                   position=request.form.get("position"))
        # Display a flash message
        flash("Employee added !")
    return redirect("/editemployee")

@app.route("/delemployee", methods=["GET", "POST"])
@login_required
def delemployee():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM employees")
        return render_template("admin/employees.html", employees=rows)
    elif request.method == "POST":
        if request.form["employeeid"]:
            db.execute("DELETE FROM employees WHERE employeeid = :employeeid", employeeid=request.form.get("employeeid"))
            # Display a flash message
            flash("Employee removed !")
        return redirect("/editemployee")

@app.route("/pviewEmployees")
@login_required
def pviewEmployees():
    rows = db.execute("SELECT * FROM employees")
    now = datetime.now()
    return render_template("admin/pview_employees.html", employees=rows, now=now)

@app.route("/printEmployees")
@login_required
def printEmployees():
    rows = db.execute("SELECT * FROM employees")
    now = datetime.now()
    return render_template("admin/print_employees.html", employees=rows, now=now)

@app.route("/editemployee", methods=["GET", "POST"])
@login_required
def editemployee():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM employees")
        return render_template("admin/editemployee.html", employees=rows)
    elif request.method == "POST":
        if request.form["employeeid"]:
            db.execute("UPDATE employees SET name = :name, lastname = :lastname, email = :email, phone = :phone, joiningDate = :joiningDate, leavingDate = :leavingDate, salary = :salary, position = :position WHERE employeeid = :employeeid",
            employeeid=request.form.get("employeeid"), name=request.form.get("name"), lastname=request.form.get("lastname"),
            email=request.form.get("email"), phone=request.form.get("phone"), joiningDate=request.form.get("joiningDate"),
            leavingDate=request.form.get("leavingDate"),  salary=request.form.get("salary"), position=request.form.get("position"))
        return redirect("/employees")
####################   ./ EMPLOYEES    ############################


####################   /CLIENTS   ##############################
@app.route("/clients")
@login_required
def clients():
    rows = db.execute("SELECT * FROM clients")
    return render_template("admin/clients.html", clients=rows)

@app.route("/editClient", methods=["GET", "POST"])
@login_required
def editClient():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM clients")
        return render_template("admin/edit_client.html", clients=rows)
    elif request.method == "POST":
        if request.form["clientid"]:
            db.execute("UPDATE clients SET name = :name, lastname = :lastname, email = :email, phone = :phone, joiningDate = :joiningDate, leavingDate = :leavingDate, salary = :salary, position = :position WHERE employeeid = :employeeid",
            employeeid=request.form.get("employeeid"), name=request.form.get("name"), lastname=request.form.get("lastname"),
            email=request.form.get("email"), phone=request.form.get("phone"), joiningDate=request.form.get("joiningDate"),
             leavingDate=request.form.get("leavingDate"),  salary=request.form.get("salary"), position=request.form.get("position"))
        return redirect("/editClient")

@app.route("/addclient", methods=["GET", "POST"])
@login_required
def addclient():
    if request.method == "GET":
        return render_template("admin/clients.html")
    elif request.method == "POST":
        if not request.form.get("name") or not request.form.get("lastname"):
            return render_template("apology.html")
        db.execute("INSERT INTO clients (name, lastname, email, phone, date) VALUES(:name, :lastname, :email, :phone, :date)",
                    name=request.form.get("name"), lastname=request.form.get("lastname"),
                    email=request.form.get("email"), phone=request.form.get("phone"),
                    date=datetime.now())
                    # Display a flash message
        flash("Client added !")
    return redirect("/editClient")

@app.route("/delclient", methods=["GET", "POST"])
@login_required
def delclient():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM clients")
        return render_template("admin/clients.html", employees=rows)
    elif request.method == "POST":
        if request.form["clientid"]:
            db.execute("DELETE FROM clients WHERE clientid = :clientid", clientid=request.form.get("clientid"))
            # Display a flash message
            flash("Client removed!")
        return redirect("/editClient")

@app.route("/pviewClients")
@login_required
def pviewClients():
    rows = db.execute("SELECT * FROM clients")
    now = datetime.now()
    return render_template("admin/pview_clients.html", clients=rows, now=now)

@app.route("/printClients")
@login_required
def printClients():
    rows = db.execute("SELECT * FROM clients")
    now = datetime.now()
    return render_template("admin/print_clients.html", clients=rows, now=now)

####################   ./ CLIENTS    ############################

####################      SITES      ############################
@app.route("/sites")
@login_required
def sites():
    rows = db.execute("SELECT * FROM sites")
    db.execute("SELECT * FROM sites")
    return render_template("admin/sites.html", sites=rows)

@app.route("/editSites", methods=["GET", "POST"])
@login_required
def editSites():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM sites")
        rows2 = db.execute("SELECT * FROM clients")
        return render_template("admin/edit_sites.html", sites=rows, clients=rows2)
    elif request.method == "POST":
        if request.form["siteid"]:
            db.execute("UPDATE clients SET name = :name, lastname = :lastname, email = :email, phone = :phone, joiningDate = :joiningDate, leavingDate = :leavingDate, salary = :salary, position = :position WHERE employeeid = :employeeid",
            employeeid=request.form.get("employeeid"), name=request.form.get("name"), lastname=request.form.get("lastname"),
            email=request.form.get("email"), phone=request.form.get("phone"), joiningDate=request.form.get("joiningDate"),
             leavingDate=request.form.get("leavingDate"),  salary=request.form.get("salary"), position=request.form.get("position"))
        return redirect("/editeSites")

@app.route("/addsite", methods=["GET", "POST"])
@login_required
def addsite():
    if request.method == "GET":
        return render_template("admin/sites.html")
    elif request.method == "POST":
        db.execute("INSERT INTO sites (country, countryCode, city, postCode, adress, clientid) VALUES(:country, :countryCode, :city, :postCode, :adress, :clientid)",
                   clientid=request.form.get("clientid"), country=request.form.get("country"), city=request.form.get("city"),
                   countryCode=request.form.get("countryCode"), postCode=request.form.get("postCode"),
                   adress=request.form.get("adress"))
                   # Display a flash message
        flash("Site added !")
        return redirect("/editSites")

@app.route("/delsite", methods=["GET", "POST"])
@login_required
def delsite():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM sites")
        return render_template("admin/sites.html", sites=rows)
    elif request.method == "POST":
        if request.form["siteid"]:
            db.execute("DELETE FROM sites WHERE siteid = :siteid", siteid=request.form.get("siteid"))
            # Display a flash message
            flash("Site deleted !")
        return redirect("/editSites")

@app.route("/pviewSites")
@login_required
def pviewSites():
    rows = db.execute("SELECT * FROM sites")
    now = datetime.now()
    return render_template("admin/pview_sites.html", sites=rows, now=now)

@app.route("/printSites")
@login_required
def printSites():
    rows = db.execute("SELECT * FROM sites")
    now = datetime.now()
    return render_template("admin/print_sites.html", sites=rows, now=now)

########################################## ./ SITES ##################################





####################     VEHICULES     ############################
@app.route("/vehicules")
@login_required
def vehicules():
    rows = db.execute("SELECT * FROM vehicules")
    db.execute("SELECT * FROM vehicules")
    return render_template("admin/vehicules.html", vehicules=rows)

@app.route("/editVehicules", methods=["GET", "POST"])
@login_required
def editVehicules():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM vehicules")
        return render_template("admin/edit_vehicules.html", vehicules=rows)
    elif request.method == "POST":
        if request.form["vehiculeid"]:
            db.execute("UPDATE vehicules SET name = :name, lastname = :lastname, email = :email, phone = :phone, joiningDate = :joiningDate, leavingDate = :leavingDate, salary = :salary, position = :position WHERE employeeid = :employeeid",
            employeeid=request.form.get("employeeid"), name=request.form.get("name"), lastname=request.form.get("lastname"),
            email=request.form.get("email"), phone=request.form.get("phone"), joiningDate=request.form.get("joiningDate"),
             leavingDate=request.form.get("leavingDate"),  salary=request.form.get("salary"), position=request.form.get("position"))
        return redirect("/editeVehicules")

@app.route("/addVehicule", methods=["GET", "POST"])
@login_required
def addVehicule():
    if request.method == "GET":
        return render_template("admin/edit_vehicules.html")
    elif request.method == "POST":
        db.execute("INSERT INTO vehicules (category, make, year, mileage, licensePlate) VALUES(:category, :make, :year, :mileage, :licensePlate)",
                   category=request.form.get("category"), make=request.form.get("make"),
                   mileage=request.form.get("mileage"), year=request.form.get("year"),
                   licensePlate=request.form.get("licensePlate"))
                   # Display a flash message
        flash("Vehicule added !")
    return redirect("/editVehicules")

@app.route("/delVehicule", methods=["GET", "POST"])
@login_required
def delVehicule():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM vehicules")
        return render_template("admin/edit_vehicules.html", vehicules=rows)
    elif request.method == "POST":
        if request.form["vehiculeid"]:
            db.execute("DELETE FROM vehicules WHERE vehiculeid = :vehiculeid", vehiculeid=request.form.get("vehiculeid"))
            # Display a flash message
            flash("Vehicule deleted !")
        return redirect("/editVehicules")

@app.route("/pviewVehicules")
@login_required
def pviewVehicules():
    rows = db.execute("SELECT * FROM vehicules")
    now = datetime.now()
    return render_template("admin/pview_vehicules.html", vehicules=rows, now=now)

@app.route("/printVehicules")
@login_required
def printVehicules():
    rows = db.execute("SELECT * FROM vehicules")
    now = datetime.now()
    return render_template("admin/print_vehicules.html", vehicules=rows, now=now)
########################## ./ VEHICULES   ##################################


######################################################################################
##
##                                      AUTH
##
######################################################################################

@app.route("/deluser", methods=["GET", "POST"])
@login_required
def deluser():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM users")
        return render_template("admin/users.html", users=rows)
    elif request.method == "POST":
        if request.form["userid"]:
            db.execute("DELETE FROM users WHERE userid = :userid", userid=request.form.get("userid"))
            # Display a flash message
            flash("User revoved !")
        return redirect("/users")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        # Remember which user has logged in
        session["user_id"] = rows[0]["userid"]
        session["user_id"] = rows[0]["username"]
        # Display a flash message
        flash("Logged in!")
        # Redirect user to home page
        return redirect(url_for("admin"))
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("auth/login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
            # Ensure password and confirmation match
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords do not match", 400)
        # hash the password and insert a new user in the database
        hash = generate_password_hash(request.form.get("password"))
        new_userid = db.execute("INSERT INTO users (username, email, hash) VALUES(:username, :email, :hash)",
                                 username=request.form.get("username"),email=request.form.get("email"),
                                 hash=hash)
        # unique username constraint violated?
        if not new_userid:
            return apology("username taken", 400)
        # Remember which user has logged in
        session["userid"] = new_userid
        # Display a flash message
        flash("User successfully added !")
        # Redirect user to home page
        return redirect(url_for("users"))
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("auth/register.html")

@app.route("/logout")
@login_required
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    return render_template("website/home.html")


@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    """Allow user to change her password"""
    if request.method == "POST":
        # Ensure current password is not empty
        if not request.form.get("current_password"):
            return apology("must provide current password", 400)
        # Query database for user_id
        rows = db.execute("SELECT hash FROM users WHERE userid = :userid", userid=session["user_id"])
        # Ensure current password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("current_password")):
            return apology("invalid password", 400)
        # Ensure new password is not empty
        if not request.form.get("new_password"):
            return apology("must provide new password", 400)
        # Ensure new password confirmation is not empty
        elif not request.form.get("new_password_confirmation"):
            return apology("must provide new password confirmation", 400)
        # Ensure new password and confirmation match
        elif request.form.get("new_password") != request.form.get("new_password_confirmation"):
            return apology("new password and confirmation must match", 400)
        # Update database
        hash = generate_password_hash(request.form.get("new_password"))
        rows = db.execute("UPDATE users SET hash = :hash WHERE userid = :userid", userid=session["user_id"], hash=hash)
        # Show flash
        flash("Password Changed!")
    return render_template("auth/changepass.html")


######################################################################################
##
##                                   WEBSITE
##
######################################################################################

@app.route("/home")
def home():
    return render_template("website/home.html")

@app.route("/services")
def services():
    return render_template("website/services.html")

@app.route("/about")
def about():
    return render_template("website/about.html")

@app.route("/project")
def project():
    return render_template("website/project.html")

@app.route("/detail")
def detail():
    return render_template("website/detail.html")

@app.route("/blog")
def blog():
    rows=db.execute("SELECT * FROM articles ORDER BY time DESC")
    return render_template("website/blog.html", articles=rows)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return render_template("website/contact.html")
    elif request.method == "POST":
        if not request.form.get("name") or not request.form.get("email"):
            return render_template("apology.html")
        db.execute("INSERT INTO messages (name, lastname, email, subject, content, dateCreated) VALUES(:name, :lastname, :email, :subject, :content, :dateCreated)",
                   name=request.form.get("name"), lastname=request.form.get("lastname"),
                   email=request.form.get("email"), subject=request.form.get("subject"),
                   content=request.form.get("content"), dateCreated=datetime.now())
        return redirect(url_for("index"))
    return render_template("website/contact.html")
########################################## ./ WEBSITE ##################################


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)