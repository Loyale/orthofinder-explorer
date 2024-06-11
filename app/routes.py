import logging
from flask import render_template, Flask#, request
from . import db
from .models import Orthogroup, Gene, Species, Sequence, GeneKeyLookup

def register_routes(app):
    @app.route('/')
    def index():
        app.logger.warning('testing warning log')
        print("Index route accessed")
        orthogroups = db.session.query(Orthogroup).all()
        return render_template('index.html', orthogroups=orthogroups)

    @app.route('/orthogroup/<orthogroup_id>')
    def orthogroup(orthogroup_id):
        print(f"Orthogroup route accessed for {orthogroup_id}")
        orthogroup = db.session.query(Orthogroup).get_or_404(orthogroup_id)
        genes = db.session.query(Gene).filter_by(orthogroup_id=orthogroup_id).all()
        return render_template('orthogroup.html', orthogroup=orthogroup, genes=genes)

    @app.route('/test')
    def test_route():
        return "This is a test route"

    @app.route('/site-map')
    def site_map():
        links = []
        for rule in app.url_map.iter_rules():
            # Filter out rules we can't navigate to in a browser
            # and rules that require parameters
            if "GET" in rule.methods and has_no_empty_params(rule):
                url = url_for(rule.endpoint, **(rule.defaults or {}))
                links.append((url, rule.endpoint))
            # links is now a list of url, endpoint tuples
