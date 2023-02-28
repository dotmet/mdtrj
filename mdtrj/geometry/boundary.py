def parse_boundary(mol, bonds, box, bl=1):
  
    bonds = bonds[np.argsort(bonds[:,0])]
    parsed_index = [0]

    for bond in bonds:
        p0 = mol[bond[0]]
        p1 = mol[bond[1]]
        _p1 = copy.deepcopy(p1)
        vec = p1-p0
        absvec = np.abs(vec)
        if bond[1] not in parsed_index:
            for i in range(3):
                if np.abs(vec[i])>box[i]/2:
                    _p1[i] = -(vec[i]/absvec[i])*box[i]+_p1[i]
            parsed_index.append(bond[1])
        mol[bond[1]] = _p1
        
    return mol
