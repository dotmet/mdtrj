
import numpy as np
from multiprocessing import Pool

from tqdm import tqdm

from copy import deepcopy

from .read_gsd import read_gsd_file

from pypolymer.util import parse_boundary

def loadfiles(fns, parse_boundary=False, read_velo=False, parallel=True, processes=10):
    '''
    Load multipule trajectorys a one time.
    '''
    
    trjs = []
    
    if parallel:
        params = []
        for i,fn in enumerate(fns):
            params.append([fn, parse_boundary, read_velo])
        
        with Pool(processes=processes) as pool:
            trjs = pool.starmap(load, params)
            pool.close()
    else:
        for fn in fns:
            trjs.append(load(fn, parse_boundary, read_velo))
    
    return trjs
        

def load(fn=None, parse_boundary=False, read_velo=False, start=0, end=None, skip=1):
    '''A smart load function can automatically determin the file type.
    
    Parameters
    ----------
    fn: trajector file name, optinal, defulat=None
    parse_boundary: bool, optional, default=True
    use_iter: bool optional, default=False
    
    Returns
    -------
    traj: mdtrj.Trajectory
    
    '''
    
    file_type = fn.split('.')[-1]
    
    if file_type in ['gsd']:
        return load_gsd(fn, parse_boundary, read_velo, start, end, skip)
    if file_type in ['lammpstrj']:
        return load_lmp(fn, parse_boundary, read_velo, start, end, skip)

def load_gsd(gsd_fn=None, parse_boundary=False, read_velo=False, start=0, end=None, skip=1):
    '''Load data from a gsd file
    
    Parameters
    ----------
    gsd_fn: gsd file name, optional, default=None
    parse_boundary: bool, optional, default=True
    use_iter: bool optional, default=False
    
    Returns
    -------
    traj: mdtrj.trajectory
    '''
    
    topo = None
    coords = None
    velos = None
    
    if gsd_fn is not None:
        
        coords, velos, topo = read_gsd_file(gsd_fn, read_velo, start, end, skip)
    
    traj = Trajectory(coords, topo, velos)
    
    if parse_boundary:
        traj.parse_boundary()
        
    return traj
    
def load_lmp(lmp_fn=None, parse_boundary=True):
    snaps = convert_to_gsd(lmp_fn, parse_boundary)
    pass

def convert_to_gsd(fn, parse_bound):
    pass

class Trajectory(object):

    ''' A class used to cache trajectory data'''
    
    def __init__(self, coords=None, topo=None, velos=None):
        ''' Initialize trajectory'''
        
        self.topology = topo
        
        self.coords = coords
        self.velos = velos

    
    def __len__(self):
        '''Get the length of trajectory'''
        return len(self.coords)
        
    def __getitem__(self, key):
        '''Get a slice of a md trajectory'''
        return self._slice(key)
    
    def _slice(self, key, copy=True):
        '''Slice a trajectory, like slice a list
        Parameters
        ----------
        key : {int, np.ndarray, slice}
            Just use it like a list
        copy : bool, default=True
            Choose to generate a new trajectory or 
            just modify current trajectory.
        '''
        
        coords = self.coords[key]
        if isinstance(self.velos, np.ndarray):
            velos = self.velos[key]
        else:
            velos = None
        
        if copy:
            _coords = deepcopy(coords)
            if self.velos is not None:
                _velos = deepcopy(velos)
            else:
                _velos = None
            topo = deepcopy(self.topology)
        
        _traj = self.__class__(_coords, topo, _velos)
        
        return _traj
        
    def parse_boundary(self, center=False, enable_tqdm=False):
        '''Read data from hoomd.trajecotry
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        print('Restore configuration broken by the PBCs [step/total steps]:')
        bonds = self.topology.bonds
        box = self.topology.box
        
        _coords = []

        if enable_tqdm:
            for i in tqdm(range(len(self.coords))):
                _crds = self.coords[i]
                crds = parse_boundary(_crds, bonds, box)
                _coords.append(crds)
            
            if center:
                for i in tqdm(range(len(_coords))):
                    _crds = _coords[i]
                    _coords[i] = _crds - np.mean(_crds, axis=0)
        else:
            for i in range(len(self.coords)):
                _crds = self.coords[i]
                crds = parse_boundary(_crds, bonds, box)
                _coords.append(crds)
            
            if center:
                for i in range(len(_coords)):
                    _crds = _coords[i]
                    _coords[i] = _crds - np.mean(_crds, axis=0)
                
        self.coords = np.array(_coords, dtype=float)
        
    def stack_coords(self):
        if isinstance(self.coords, list):
            _coords = self.coords
        else:
            _coords = []
            for crd in self.coords:
                _coords.append(crd)
                
        self.coords = (_ for _ in _coords)
        
        return np.array(_coords, dtype=float)
        
    def stack_velos(self):
    
        _velos = []
        for v in self.velos:
            _velos.append(v)
        self.velos = (_ for _ in _velos)
        
        return np.array(_velos, dtype=float)
