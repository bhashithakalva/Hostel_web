print("RUNNING FILE:", __file__)
from flask import Flask, render_template, request, redirect, session, url_for
from authlib.integrations.flask_client import OAuth
import os
from firebase_config import db


app = Flask(__name__)
app.secret_key = "hostel_secret"

from authlib.integrations.flask_client import OAuth

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id="43413393142-qaqfj8vu0cb4p1bsb7s29bhavvil9h2v.apps.googleusercontent.com ",
    client_secret="{'web'':{'client_id':'43413393142-qaqfj8vu0cb4p1bsb7s29bhavvil9h2v.apps.googleusercontent.com','project_id':'hostel-management-483411','auth_uri':'https://accounts.google.com/o/oauth2/auth','token_uri':'https://oauth2.googleapis.com/token','auth_provider_x509_cert_url':https://www.googleapis.com/oauth2/v1/certs','client_secret':'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','redirect_uris':['http://127.0.0.1:5000/callback'],'javascript_origins':['http://127.0.0.1:5000']}}",
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    client_kwargs={"scope": "openid email profile"},
)
@app.route('/login/google')
def login_google():
    redirect_uri = url_for('authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize/google')
def authorize_google():
    token = google.authorize_access_token()
    user = google.get('userinfo').json()

    email = user['email']

    if email.endswith('@siddhartha.edu.in') or email.endswith('@vrsec.ac.in'):
        session['email'] = email
        return redirect('/student')
    else:
        return "Only college email allowed"



@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")

        # allowed college domains
        allowed_domains = (
            "@siddhartha.edu.in",
            "@vrsec.ac.in"
        )

        if email and email.endswith(allowed_domains):
            session["email"] = email

            # simple role check
            if email.startswith("staff"):
                return redirect("/staff")
            else:
                return redirect("/student")
        else:
            return "❌ Please use your college email (@siddhartha.edu.in or @vrsec.ac.in)"

    return render_template("login.html")



@app.route("/student")
def student():
    if "email" not in session:
        return redirect("/")

   
    doc = db.collection("food").document("today").get()

    if doc.exists:
        data = doc.to_dict()
        food = data.get("ready", "Not updated")
        items = data.get("items", "Not updated")
    else:
        food = "Not updated"
        items = "Not updated"

    
    return render_template(
        "student.html",
        food=food,
        items=items
    )


from datetime import date

@app.route("/attendance", methods=["POST"])
def attendance():
    today = str(date.today())

    db.collection("attendance").add({
        "student": session.get("email", "unknown"),
        "date": today
    })

    return redirect("/student")


@app.route("/staff", methods=["GET", "POST"])
def staff():
    if "email" not in session:
        return redirect("/")

    if request.method == "POST":
        food = request.form.get("food")
        items = request.form.get("items")

        db.collection("food").document("today").set({
            "ready": food,
            "items": items
        })
        return redirect("/staff")
    return render_template("staff.html")



@app.route("/complaint", methods=["POST"])
def complaint():
    db.collection("complaints").add({
        "student": session["email"],
        "text": request.form["complaint"]
    })
    return redirect("/student")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
if __name__ == "__main__":
    app.run(debug=True)
from datetime import date

@app.route("/complaint", methods=["POST"])
def complaint():
    text = request.form.get("complaint")

    if text:
        db.collection("complaints").add({
            "student": session.get("email", "unknown"),
            "complaint": text
        })

    return redirect("/student")

@app.route("/logout")
def logout():
    return "LOGOUT ROUTE HIT"
