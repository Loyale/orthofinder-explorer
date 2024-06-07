from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import Base, Orthogroup, Gene, Sequence, Species, GeneKeyLookup

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/orthofinder.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        # Ensure tables are created
        from sqlalchemy import create_engine
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        Base.metadata.create_all(engine)
        
        from . import routes

    return app