#!/usr/bin/env python
#%%
import pandas as pd 
from ete3 import Tree
import os 
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Orthogroup, Gene, Sequence, Species, GeneKeyLookup

#%%
OFDir = '../data/Results_May02'
verbose=True
##########
# Parsing
##########
#%% Orthogroups
def parse_orthogroups(orthogroups_file,verbose=False):
    if verbose:
        print (f"Reading orthogroups from {orthogroups_file}")
    orthogroups_df = pd.read_csv(orthogroups_file, sep='\t')
    orthogroups_df = orthogroups_df.melt(id_vars=['Orthogroup'])
    orthogroups_df.columns = ['orthogroup', 'species', 'genes']
    orthogroups_df['genes'] = orthogroups_df['genes'].str.split(',')
    return orthogroups_df

orthogroups_file = OFDir + '/Orthogroups/Orthogroups.tsv'
orthogroups_df = parse_orthogroups(orthogroups_file)

#orthogroups_df
orthogroup_list = orthogroups_df['orthogroup'].unique()

#%% Species
def strip_file_extension(filename):
    root, ext = os.path.splitext(filename)
    return root

def parse_species_file(species_file, verbose=False):
    if verbose:
        print(f"Reading species info from {species_file}")
    species_df = pd.read_csv(species_file, sep=': ', header=None)
    species_df.columns = ['species_id', 'species']
    species_df.species = species_df.species.apply(strip_file_extension)
    return species_df

species_file = OFDir + '/WorkingDirectory/SpeciesIDs.txt'
species_df = parse_species_file(species_file)

#%% Merge orthogroups_df with species_df
orthogroups_df = orthogroups_df.merge(species_df,on="species")

#%% Species trees
def get_species_tree(species_tree_file, verbose=False):
    if verbose:
        print(f"Reading species tree from {species_tree_file}")
    for line in open(species_tree_file):
        species_tree = line.strip()
        species_tree = Tree(species_tree)
    return species_tree

species_tree_file = OFDir + '/Species_Tree/SpeciesTree_rooted.txt'
species_tree = get_species_tree(species_tree_file)

#%% Get protein sequences
# Multi-gene fasta parser that outputs a pandas df
def parse_protein_sequence_file(protein_sequence_file):
    fasta = open(protein_sequence_file).read().split('>')
    protein_sequences = []
    for entry in fasta[1:]:
        entry = entry.split('\n')
        protein_id = entry[0]
        protein_sequence = ''.join(entry[1:])
        protein_sequences.append([protein_id, protein_sequence])
    protein_sequences_df = pd.DataFrame(protein_sequences, columns=['protein_id', 'protein_sequence'])
    return protein_sequences_df

def get_protein_sequences(species_df,verbose=False):
    if verbose:
        print("Reading protein sequences")
    sequences = []
    for index, row in species_df.iterrows():
        species_of_id = row['species_id']
        print(f"\tFetching {row['species']}")
        protein_sequence_file = OFDir + f'/WorkingDirectory/Species{species_of_id}.fa'
        protein_sequences_df = parse_protein_sequence_file(protein_sequence_file)
        sequences.append(protein_sequences_df)
    sequences_df = pd.concat(sequences)
    sequences_df.reset_index(drop=True, inplace=True)
    sequences_df.set_index('protein_id', inplace=True)
    return sequences_df

sequences_df = get_protein_sequences(species_df)
    
#%%
##################
# DBase setup
##################
#%% SQLite setup
engine = create_engine('sqlite:///../instance/orthofinder.db')

#%% mySQL setup
# engine = create_engine('mysql+pymysql://user:password@localhost/orthofinder')

#%%
# Create all tables
print("Creating tables")
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

######################
# Load Data into DBase
######################
def load_data():
    pass
#%% Orthogroup_list
print("Loading orthogroups into database")
for orthogroup in orthogroup_list:
    orthogroup = Orthogroup(orthogroup_id=orthogroup)
    session.add(orthogroup)

session.commit()
#%% Genes
print("Loading genes into database")
for index, row in orthogroups_df.iterrows():
    if isinstance(row['genes'], list) and row['genes']:  # Check if the list is not empty
        for gene_id in row['genes']:
            gene = Gene(gene_id=gene_id, orthogroup_id=row['orthogroup'], species_id = row['species_id'])
            session.add(gene)

session.commit()
#%% Species
print("Loading species into database")
for index, row in species_df.iterrows():
    species = Species(species_id=row['species_id'], species_name=row['species'])
    session.add(species)

session.commit()

##############
# Update orthogroups table with gene trees
##############
#%% get gene trees
# A generator to retrieve orthogroup gene trees one at a time

def get_gene_trees(orthogroups_list, gene_tree_dir, verbose=False):
    if verbose:
        print(f"Reading gene trees from {gene_tree_dir}")
    for orthogroup in orthogroups_list:
        gene_tree_file = os.path.join(gene_tree_dir, f'{orthogroup}_tree.txt')
        if os.path.exists(gene_tree_file):
            with open(gene_tree_file) as f:
                gene_tree = f.read().strip()
                gene_tree = Tree(gene_tree)  # Assuming Tree is defined elsewhere
                yield orthogroup, gene_tree
        else:
            print(f"Warning: Gene tree for {orthogroup} was not found.")

gene_tree_dir = OFDir + '/Gene_Trees/'
gene_tree_iter = get_gene_trees(orthogroup_list, gene_tree_dir)

#%%
# Inserting or updating orthogroup gene_tree data into the database
print("Loading gene trees into database")
for ortho, gene_tree in gene_tree_iter:
    # Fetch the existing orthogroup if it exists
    orthogroup = session.query(Orthogroup).filter_by(orthogroup_id=ortho).first()
    
    if orthogroup is None:
        # Insert a new orthogroup if it doesn't exist
        orthogroup = Orthogroup(orthogroup_id=ortho, gene_tree=gene_tree.write())
        session.add(orthogroup)
    else:
        # Update the description of the existing orthogroup
        #orthogroup.description = row['Description']
        orthogroup.gene_tree = gene_tree.write()
# Commit the changes to the database
session.commit()
# %%
print("Done!")
