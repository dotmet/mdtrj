import numpy as np

class Topology(object):
    '''
        A class stores the topological information of a system.
    '''

    def __init__(self):
        
        self.atoms = 0
        self.atom_types = []
        self.masses = []
        
        self.bonds = []
        self.angles = []
        self.dihedrals = []
        self.box = []