import fresnel
import math
import matplotlib, matplotlib.cm
import matplotlib.pyplot as plt
import numpy
import mdtrj
import PIL

def render_polymer_coords(position, view='isometric', cmap_name='viridis', size=(450, 450), cheight=None, adjust=False, show=True):
    
    device = fresnel.Device()
    scene = fresnel.Scene(device)

    geometry = fresnel.geometry.Sphere(scene, position = position, radius=0.5)
    geometry.material = fresnel.material.Material(primitive_color_mix=1.0, color=(1,1,1))
    

    mapper = matplotlib.cm.ScalarMappable(norm = matplotlib.colors.Normalize(vmin=0, vmax=1, clip=True),
                                        cmap = matplotlib.cm.get_cmap(name=cmap_name))

    v = numpy.linspace(0,1,len(position))
    geometry.color[:] = fresnel.color.linear(mapper.to_rgba(v))
    
    if view in ['xoy', 'xoz', 'yoz']:
        
        idxs = None
        cposi = [0, 0, 0]
        up = [0, 0, 0]
        
        if view == 'xoz':
            idxs = [0, 2, 1]
            cposi[idxs[2]] = numpy.min(position[:,idxs[2]]) - 1
        elif view == 'xoy':
            idxs = [0, 1, 2]
            cposi[idxs[2]] = numpy.max(position[:,idxs[2]]) + 1
        elif view == 'yoz':
            idxs = [1, 2, 0]
            cposi[idxs[2]] = numpy.min(position[:,idxs[2]]) - 1
        
        side0 = position[:, idxs[0]]
        side1 = position[:, idxs[1]]
        L_side0 = numpy.max(side0) - numpy.min(side0)
        L_side1 = numpy.max(side1) - numpy.min(side1)
        L = (L_side0, L_side1)
        
        min_side = 0 if L_side0 < L_side1 else 1
        max_side = numpy.abs(1-min_side)
        
        
        if adjust or (size[min_side]/size[max_side]<L[min_side]/L[max_side]):
            _size = [size[0], size[1]]
            _size[min_side] = int(_size[max_side]*(L[min_side]/L[max_side])) + int(1.5*_size[max_side]/L[max_side])
            size = (size[max_side], _size[min_side])
        
        _h = L[max_side]
        if (cheight is None) or (cheight < _h):
            cheight = _h
        
        up[idxs[1]] = 1
        if size[0] != size[1]:
            cheight = cheight*(size[min_side]/size[max_side])
            
        # cheight = cheight
        
        scene.camera = fresnel.camera.Orthographic(position=cposi, look_at=-numpy.array(cposi), up=up, height=cheight+1)
        
    elif view in ['auto', 'isometric', 'front']:
        scene.camera = fresnel.camera.Orthographic.fit(scene, view=view)
        
    else:
        raise ValueError(f'Wrong view parameter choosed : "{view}"')

    scene.lights.append(fresnel.light.Light(direction=(0,0,1), color=(1,1,1), theta=3.14))
    scene.background_color = (1, 1, 1)
    
    w, h = size
    out = fresnel.pathtrace(scene, samples=64,
                            light_samples=32,
                            w=w, h=h)
    if show:
        PIL.Image.fromarray(out[:], mode='RGBA').show()
        
    return out

def visualize_polymer(position, out=None, view='xoz', ax=None, matplot=False, cmap_name='viridis', size=(8000,8000), cposi=[0, -20, 0], cheight=20):
    
    if ax is None and matplot:
        fig, ax = plt.subplots(1,1)
    
    if out is None:
        out = render_polymer_coords(position, view, cmap_name, size, cposi, cheight, show=False)
    
    if ax is not None:
    
        ax.imshow(out[:])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        return ax
    
    else:
        PIL.Image.fromarray(out[:], mode='RGBA').show()
        return out[:]