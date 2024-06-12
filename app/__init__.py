from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import Base, Orthogroup, Gene, Sequence, Species, GeneKeyLookup
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'orthofinder.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        # Ensure tables are created
        from sqlalchemy import create_engine
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        Base.metadata.create_all(engine)

        #print("App and DB initialized")
        from .routes import register_routes
        register_routes(app)
        
        # Unomment to see all routes
        #for rule in app.url_map.iter_rules():
        #    print(rule)
    return app