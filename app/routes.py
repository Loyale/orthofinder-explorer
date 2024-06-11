import logging
from flask import render_template, request
from markupsafe import Markup
from sqlalchemy import func
from . import db
from .models import Orthogroup, Gene, Species, Sequence, GeneKeyLookup
from ete3 import Tree, TreeStyle, NodeStyle, faces, AttrFace, TreeFace, TextFace
from io import BytesIO
import base64
import os
from tempfile import NamedTemporaryFile

def register_routes(app):
    @app.route('/')
    def index():
        app.logger.warning('testing warning log')
        print("Index route accessed")
        orthogroups = db.session.query(Orthogroup).all()
        return render_template('index.html', orthogroups=orthogroups)

    @app.route('/orthogroup/<orthogroup_id>')
    def orthogroup(orthogroup_id):
        orthogroup = db.session.query(Orthogroup).get_or_404(orthogroup_id)
        genes = db.session.query(Gene).filter_by(orthogroup_id=orthogroup_id).all()

        # Get the Newick-formatted gene tree from the orthogroup
        gene_tree_data = orthogroup.gene_tree

        # Render the tree using ete3
        tree = Tree(gene_tree_data)
        ts = TreeStyle()
        ts.show_leaf_name = False

        # Build HTML for the tree
        def render_node(node):
            if node.is_leaf():
                url = f"/gene/{node.name}"
                return f'<li><a href="{url}">{node.name}</a></li>'
            else:
                children = ''.join(render_node(child) for child in node.children)
                return f'<li>{node.name}<ul>{children}</ul></li>'

        tree_html = f'<ul>{render_node(tree)}</ul>'
        tree_html = Markup(tree_html)

        return render_template('orthogroup.html', orthogroup=orthogroup, genes=genes, tree_html=tree_html)

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
