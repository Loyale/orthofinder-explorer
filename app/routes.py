import logging
from flask import render_template, request, send_file
from sqlalchemy import func
from . import db
from .models import Orthogroup, Gene, Species, Sequence, GeneKeyLookup
from ete3 import Tree, TreeStyle, NodeStyle, faces, AttrFace, TreeFace, TextFace
import matplotlib.pyplot as plt
import matplotlib
from tempfile import NamedTemporaryFile


# Use Agg backend to avoid issues with Flask
matplotlib.use('Agg')

def register_routes(app):
    @app.route('/')
    def index():
        app.logger.warning('testing warning log')
        print("Index route accessed")
        orthogroups = db.session.query(Orthogroup).all()
        return render_template('index.html', orthogroups=orthogroups)

    @app.route('/orthogroup_ete/<string:orthogroup_id>')
    def orthogroup_ete(orthogroup_id):
        orthogroup = db.session.query(Orthogroup).filter_by(orthogroup_id=orthogroup_id).first_or_404()

        tree_image = None
        if orthogroup.gene_tree:
            tree = Tree(orthogroup.gene_tree)
            ts = TreeStyle()
            ts.show_leaf_name = True
            #ts.scale=200
            ts.branch_vertical_margin = 10

            # Render the tree to a list of strings
            svg_str_list = tree.render(file_name="%%return", w=800, tree_style=ts)
            svg_str = "".join([str(element) for element in svg_str_list if isinstance(element, str)])

            # Clean up the SVG string
            svg_str = svg_str.replace("\\n", "").replace("b'", "").replace("'","")

            tree_image = svg_str

        return render_template('orthogroup_ete.html', orthogroup=orthogroup, tree_image=tree_image)

    @app.route('/orthogroup/<string:orthogroup_id>')
    def orthogroup(orthogroup_id):
        orthogroup = db.session.query(Orthogroup).filter_by(orthogroup_id=orthogroup_id).first_or_404()
        return render_template('orthogroup.html', orthogroup=orthogroup)

    @app.route('/orthogroups', methods=['GET', 'POST'])
    def orthogroups():
        search_query = request.form.get('search_query', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.form.get('per_page', 10, type=int)

        print(f"Search query: {search_query}")
        print(f"Page: {page}")
        print(f"Per page: {per_page}")

        query = db.session.query(Orthogroup)
        if search_query:
            query = query.filter(Orthogroup.orthogroup_id.ilike(f'%{search_query}%'))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        orthogroups = pagination.items

        print(f"Orthogroups: {orthogroups}")

        return render_template('orthogroups.html', orthogroups=orthogroups, pagination=pagination, search_query=search_query, per_page=per_page)
    
    @app.route('/gene_search', methods=['GET', 'POST'])
    def gene_search():
        if request.method == 'POST':
            search_query = request.form.get('search_query')
            # Perform a case-insensitive search
            genes = db.session.query(Gene).filter(Gene.gene_id.ilike(f"%{search_query}%")).all()
            orthogroups = {gene.orthogroup_id: gene for gene in genes}
            return render_template('gene_search_results.html', genes=genes, orthogroups=orthogroups)
        return render_template('gene_search.html')
    
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
