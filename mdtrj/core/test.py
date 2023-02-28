from trajectory import *

import gsd.hoomd
import matplotlib.pyplot as plt


gsd_fn = '20_10_1_v10.0.gsd'

snaps = gsd.hoomd.open(gsd_fn)

trj = load(gsd_fn, parse_bound=True, iter=True)

print(len(trj))

new_trj = trj[1:100]
print(len(new_trj))

for snap, tj in zip(snaps, trj.coords):
    _ps = snap.particles.position
    if np.sum(_ps-tj)!=0:
        plt.scatter(_ps[:,0], _ps[:,1])
        plt.show()
        plt.scatter(tj[:,0], tj[:,1])
        plt.show()