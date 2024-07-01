#!/usr/bin/env python
#%%
import pandas as pd 
from ete3 import Tree
import os 
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Orthogroup, Gene, Sequence, Species, GeneKeyLookup

#%%
OFDir = '../data/Results_Jun25'
verbose=True
##########
# Parsing
##########
#%% Generic multi-fasta parser
def fasta_generator(fasta_file):
    with open(fasta_file) as f:
        header = None
        sequence = ''
        for line in f:
            if line.startswith('>'):
                if header:
                    yield header, sequence
                header = line.strip().lstrip('>')
                sequence = ''
            else:
                sequence += line.strip()
        yield header, sequence

#%% Orthogroups
def parse_orthogroups(orthogroups_file,verbose=False):
    if verbose:
        print (f"Reading orthogroups from {orthogroups_file}")
    orthogroups_df = pd.read_csv(orthogroups_file, sep='\t')
    orthogroups_df = orthogroups_df.melt(id_vars=["HOG","OG","Gene Tree Parent Clade"])
    #print(orthogroups_df.head())
    orthogroups_df.columns = ["hierarchical_orthogroup","orthogroup","parent_clade"'orthogroup', 'species', 'genes']
    orthogroups_df['genes'] = orthogroups_df['genes'].str.split(',')
    return orthogroups_df

#orthogroups_file = OFDir + '/Orthogroups/Orthogroups.tsv'
orthogroups_file = OFDir + '/Phylogenetic_Hierarchical_Orthogroups/N0.tsv'
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
    protein_sequences = []
    for protein in fasta_generator(protein_sequence_file):
        species_id, ortho_protein_id = protein[0].split("_")
        protein_sequences.append((species_id, ortho_protein_id, protein[1]))
    return protein_sequences

def get_protein_sequences(species_df,verbose=False):
    if verbose:
        print("Reading protein sequences")
    sequences = []
    for index, row in species_df.iterrows():
        species_of_id = row['species_id']
        print(f"\tFetching {row['species']}")
        protein_sequence_file = OFDir + f'/WorkingDirectory/Species{species_of_id}.fa'
        protein_sequences = parse_protein_sequence_file(protein_sequence_file)
        protein_sequences_df = pd.DataFrame(protein_sequences, columns=['species_id', 'ortho_gene_id', 'protein_sequence'])
        sequences.append(protein_sequences_df)
    sequences_df = pd.concat(sequences)
    sequences_df.reset_index(drop=True, inplace=True)
    return sequences_df

def parse_sequence_ids(sequence_id_file):
    sequenceIDs = pd.read_csv(sequenceIDFile, sep=': ', header=None)
    sequenceIDs.columns = ['ortho_id', 'gene_id']
    sequenceIDs[['species_id','ortho_gene_id']] = sequenceIDs['ortho_id'].str.split("_", expand=True)
    return sequenceIDs

sequences_df = get_protein_sequences(species_df)

sequenceIDFile = OFDir + "/WorkingDirectory/SequenceIDs.txt"
sequence_ids = parse_sequence_ids(sequenceIDFile)
#print(sequence_ids.head())
sequences_df = sequences_df.merge(sequence_ids, on=['species_id', 'ortho_gene_id'], how='inner')
#print(sequences_df)

#%%
##################
# DBase setup
##################
#%% SQLite setup
engine = create_engine('sqlite:///../instance/orthofinder_new.db')

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
        prev_gene_id = None
        for gene_id in row['genes']:
            gene_id = gene_id.strip()
            if gene_id == prev_gene_id:
                print(gene_id)
            prev_gene_id = gene_id
            try:
                gene = Gene(gene_id=gene_id, orthogroup_id=row['orthogroup'], species_id = row['species_id'])
            except:
                print(gene_id)
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

#Commit the changes to the database
session.commit()

#%% Protein Sequences
print("Loading protein sequences into database")
for index, row in sequences_df.iterrows():
    sequence = Sequence(sequence_idx=row.name, 
                        species_id=row['species_id'], 
                        ortho_gene_id=row['ortho_gene_id'],
                        ortho_id=row['ortho_id'],
                        gene_id=row['gene_id'],
                        protein_sequence=row['protein_sequence'])
    session.add(sequence)

# Commit the changes to the database
session.commit()


# %%
print("Done!")
