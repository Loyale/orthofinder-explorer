#!usr/bin/env python
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey

Base = declarative_base()

class Orthogroup(Base):
    __tablename__ = 'orthogroups'
    orthogroup_id = Column(String, primary_key=True)
    gene_tree = Column(String)
    description = Column(String)

class Gene(Base):
    __tablename__ = 'genes'
    gene_id = Column(String, primary_key=True)
    ortho_gene_id = Column(String)
    orthogroup_id = Column(String, ForeignKey('orthogroups.orthogroup_id'))
    species_id = Column(String, ForeignKey('species.species_id'))
    gene_name = Column(String)

class Sequence(Base):
    __tablename__ = 'sequences'
    sequence_id = Column(String, primary_key=True)
    ortho_sequence_id = Column(String)
    gene_id = Column(String, ForeignKey('genes.gene_id'))
    protein_sequence = Column(String)
    mrna_sequence = Column(String)

class Species(Base):
    __tablename__ = 'species'
    species_id = Column(Integer, primary_key=True)
    species_name = Column(String)

class GeneKeyLookup(Base):
    __tablename__ = 'gene_key_lookup'
    of_gene_id = Column(String, primary_key=True)
    species_id = Column(Integer, ForeignKey('species.species_id'))
    species_of_index = Column(Integer)
    gene_id = Column(String, ForeignKey('genes.gene_id'))