#!/usr/bin/env python

################
# File parsers
################
# Generator for Multiple-sequence fasta parser
def fasta_generator(fasta_file):
    with open(fasta_file) as f:
        header = None
        sequence = ''
        for line in f:
            if line.startswith('>'):
                if header:
                    yield header, sequence
                header = line.strip()
                sequence = ''
            else:
                sequence += line.strip()
        yield header, sequence

# Generator for Gff3 parsing
def gff3_generator(gff3_file):
    with open(gff3_file) as f:
        for line in f:
            if line.startswith('#'):
                continue
            line = line.strip().split('\t')
            yield line