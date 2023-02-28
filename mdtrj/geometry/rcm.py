# import jax.numpy as jnp 
''' Pure numpy is much faster than jax.numpy '''
import numpy as jnp

def compute_rcm(trj):
    
    if isinstance(trj, list):
        
        all_rcms = []
        
        for _trj in trj:
            
            rcms = _compute_rcm(_trj)
            
            all_rcms.append(rcms)
        
        return all_rcms
    
    else:
        
        return _compute_rcm(trj)

def _compute_rcm(trj):
    
    rcms = []
    
    masses = trj.topology.masses
    
    total_mass = 0
    
    if not isinstance(masses, float):
    
        masses = jnp.array([masses, masses, masses]).T
        total_mass = jnp.sum(masses)
        
    else:
        total_mass = masses*trj.topology.atoms
        
    for coord in trj.coords:
    
        rcm = jnp.sum(masses*coord, axis=0)/total_mass
        rcms.append(rcm)
        
    return jnp.array(rcms)