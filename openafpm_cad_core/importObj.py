"""
Module to export to Wavefront .obj format.

See:
  `Wavefront .obj file <https://en.wikipedia.org/wiki/Wavefront_.obj_file>`_

Adapted from:
  https://github.com/FreeCAD/FreeCAD/blob/0.19.1/src/Mod/Arch/importOBJ.py#L149-L273

Adapting this code is somewhat of a hack, but in the future we will use glTF instead. 

Modifications:
  * Use object Label instead of Name for object name.
  * Remove mtl or materials generation.
  * Return .obj file contents as string instead of writing to a file.
  * Removed support of experimental high-resolution Arch feature.
    * See: https://forum.freecadweb.org/viewtopic.php?t=21144
  * Removed any code paths requiring FreeCAD's GUI to be active.
    * This script is meant to be ran from a server environment only.
  * Remove support for meshes and "Mesh Feature" objects.
    * See: https://wiki.freecadweb.org/Mesh_Feature
"""

from typing import Callable, List, Tuple

import FreeCAD as App
import MeshPart

from .resolve_objects import resolve_objects

__all__ = ['export']


def export(export_list: List[object],
           object_name_getter: Callable[[object, List[object]], str] = lambda obj, path: obj.Label,
           keep_unresolved: Callable[[object, List[object]], bool] = None) -> str:
    """
    Transforms a list of objects into a Wavefront .obj file contents.
    """
    lines = []

    offsetv = 1
    offsetvn = 1

    resolved_objects = resolve_objects(export_list, keep_unresolved)
    for resolved_object in resolved_objects:
        obj = resolved_object['object']
        placement = resolved_object['placement']
        path = resolved_object['path']
        shape = obj.Shape.copy(False)
        shape.Placement = placement

        vlist, vnlist, flist = _get_indices(shape, offsetv, offsetvn)

        offsetv += len(vlist)
        offsetvn += len(vnlist)
        object_name = object_name_getter(obj, path)
        if type(object_name) != str:
            raise ValueError('object_name_getter must return string.')
        lines.append('o ' + object_name)

        for v in vlist:
            lines.append('v ' + v)
        for vn in vnlist:
            lines.append('vn ' + vn)
        for f in flist:
            lines.append('f ' + f)
    return '\n'.join(lines) + '\n'


def _get_indices(shape, offsetv: int, offsetvn: int) -> Tuple[List[str], List[str], List[str]]:
    """
    Return a tuple containing 3 lists:

        1. vertexes
        2. vertex normals
        3. and face indices

    offset with a given amount.
    """
    vlist = []
    vnlist = []
    flist = []

    # Triangulates shapes with curves
    mesh = MeshPart.meshFromShape(
        Shape=shape, LinearDeflection=0.1, AngularDeflection=0.7, Relative=True)
    for v in mesh.Topology[0]:
        vlist.append(str(round(v[0], 6)) + ' ' +
                     str(round(v[1], 6)) + ' ' +
                     str(round(v[2], 6)))

    for vn in mesh.Facets:
        vnlist.append(str(vn.Normal[0]) + ' ' +
                      str(vn.Normal[1]) + ' ' +
                      str(vn.Normal[2]))

    for i, vn in enumerate(mesh.Topology[1]):
        flist.append(str(vn[0] + offsetv) + '//' +
                     str(i + offsetvn) + ' ' +
                     str(vn[1] + offsetv) + '//' +
                     str(i + offsetvn) + ' ' +
                     str(vn[2] + offsetv) + '//' +
                     str(i + offsetvn))

    return vlist, vnlist, flist
