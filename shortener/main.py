import atexit
import os
import random
import string
import re
import requests

from dotenv import load_dotenv
import validators
from flask import Flask, request
import flask

import database
import utils

#import global_utils

# Load my .env file :)
load_dotenv()

app = Flask(
    'app', 
    template_folder="shortener/template/",
    static_folder="shortener/static/"
)

app.secret_key = os.environ['FLASK_SECRET_KEY']

conn_params = {
    "dbname": "felixgao_dev_url_shortener",
    "user": "felixgao",
    "password": os.environ['DB_PASSWORD'],
    "host": "hackclub.app",
    "port": "5432"
}

db = database.Database(conn_params)
virus_checker = utils.CheckViruses()


@app.route('/')
def landing_page():
    return flask.render_template("index.html", cf_sitekey=os.environ['TURNSTILE_SITEKEY'])


@app.route('/analytics/<analytics_path>')
def analytics(analytics_path):
    result = db.get_analytics(analytics_path)
    if not result:
        return flask.abort(404)
    else:
        return flask.render_template("analytics.html", analytics=result)


@app.route('/<url_path>')
@app.route('/u/<url_path>')
def url_shortener(url_path):
    result = db.get_url(url_path)
    if not result:
        return flask.abort(404)
    redirect_url = result[0][1] # This is the url to redirect to

    domains = db.get_hostname(result[0][0]) # url_id
    if not domains:
        raise ValueError(f"No domains found for URL ID {result[0][0]}")
    for domain in domains:
        if request.host_url.startswith(domain[1]):
            break
    else: # Not in the right domain so 404 it lol
        return flask.abort(404)

    db.add_analytics(
        int(result[0][0]), # URL ID
        request.referrer,
        request.headers.get('User-Agent')
    )

    # Note to self: HTTP 302 = temp redirect, don't use HTTP 301 it breaks everything D:
    if not redirect_url.startswith("https://") or redirect_url.startswith("http://"):
        redirect_url = "https://" + redirect_url
    return flask.redirect(redirect_url, code=302) # Temp redirect


@app.route('/create_url', methods=["POST"])
def _api_url_creator():
    error_state = False
    new_url = request.form.get("shortened-link-field")
    old_url = request.form.get("original-link-field")
    url_blahaj_click = request.form.get("hostname-blahaj-click")
    url_dino_icu = request.form.get("hostname-dino-icu")
    turnstile_key = request.form.get("cf-turnstile-response")

    # Checks go burr
    if any(var is None for var in [old_url, turnstile_key]): # If any value is None
        return flask.abort(400) # HTTP 400: bad req - missing data

    print(url_dino_icu, url_blahaj_click)
    if url_blahaj_click is None and url_dino_icu is None:
        return flask.abort(400)

    url_hostnames = ""
    url_hostnames += url_blahaj_click + " " if url_blahaj_click else ""
    url_hostnames += url_dino_icu if url_dino_icu else ""

    for url in url_hostnames.split(" "):
        if url not in os.environ['ALLOWED_HOSTNAMES'].split(" "):
            return flask.abort(400) # HTTP 400: bad req - bad data

    # Validate turnstile key
    data = {
        "secret": os.environ['TURNSTILE_SECRET'],
        "response": turnstile_key
    }
    r = requests.post("https://challenges.cloudflare.com/turnstile/v0/siteverify", data=data)
    r.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
    result = r.json()

    if not result["success"]:
        flask.flash("Please double-check the human verification below and complete it if not already done.", "global-error")
        return flask.redirect(flask.url_for('landing_page'))

    if virus_checker.check_viruses(old_url): # Block shortening attempts which may be viruses
        flask.flash("This link can't be shortened because it may be malicious.", "original-link-error")
        return flask.redirect(flask.url_for('landing_page'))

    forbidden_url_paths = ["api", "analytics", "analytic", "admin", "login", "dashboard", "settings", "manage", "create_url", "u", "url", "shortened_url", "analytics_url", "create_url", "original_url", "id", "url_id", "referrer", "user_agent", "domains", "domain", "urls"]
    if new_url.lower() in forbidden_url_paths:
        flask.flash("That shortened URL path is reserved!", "shortened-link-error")
        error_state = True

    if not re.compile(r'^[a-zA-Z0-9-_]+$').match(new_url):
        flask.flash("Whoops! The URL can only contain alphanumeric characters, dashes, and underscores.", "shortened-link-error")
        error_state = True

    if len(new_url) > 255:
        flask.flash("Woah wheres the end? The shortened URL path is too long.", "shortened-link-error")
        error_state = True

    if db.check_url_exists("shortened_url", new_url):
        flask.flash("Sorry, that shortened URL has already been taken! Our database hates twins.", "shortened-link-error")
        error_state = True

    if not old_url.startswith("https://") or not old_url.startswith("http://"): # Not a check but instead just appends https:// if not already there
        old_url = "https://" + old_url

    if isinstance(validators.url(old_url), validators.utils.ValidationError):
        flask.flash("That's an invalid URL. Does it start with https://?", "original-link-error")
        error_state = True

    if error_state:
        return flask.redirect(flask.url_for('landing_page'))

    while True:
        analytics_url = "".join(
            # Generate a 10 character string of alphanumeric characters
            random.choice(string.ascii_letters + string.digits) for _ in range(10)
        )
        if not db.check_url_exists("analytics_url", analytics_url):
            break

    db.add_url(old_url, new_url, analytics_url, url_hostnames.split(" ")) # Add DB entry
    print([f"https://{hostname}/{new_url}" for hostname in url_hostnames.split(" ")])
    print(url_hostnames)
    return flask.render_template(
        "url_created.html",
        shortened_url=f"https://url.felixgao.dev/u/{new_url}",
        analytics_url=f"https://url.felixgao.dev/analytics/{analytics_url}",
        generated_urls= enumerate([f"https://{hostname}/{new_url}" for hostname in url_hostnames.split(" ")])
    ), 201


# Close the database on code end
atexit.register(lambda: db.close())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ['PORT_URL_SHORTENER']), debug=True)
