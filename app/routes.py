from flask import render_template, request, Flask
from . import create_app, db
from .models import Orthogroup, Gene, Species, Sequence, GeneKeyLookup

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, world"
# def index():
#     orthogroups = db.session.query(Orthogroup).all()
#     return render_template('index.html', orthogroups=orthogroups)


@app.route('/orthogroup/<orthogroup_id>')
def orthogroup(orthogroup_id):
    orthogroup = db.session.query(Orthogroup).get_or_404(orthogroup_id)
    genes = db.session.query(Gene).filter_by(orthogroup_id=orthogroup_id).all()
    return render_template('orthogroup.html', orthogroup=orthogroup, genes=genes)