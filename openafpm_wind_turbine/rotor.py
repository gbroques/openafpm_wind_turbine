import os

import Draft
import FreeCAD as App
import FreeCADGui as Gui

from .common import (enforce_recompute_last_spreadsheet, find_object_by_label,
                     make_compound)

__all__ = ['make_rotors']


def make_rotors(base_path,
                has_separate_master_files,
                document,
                coil_inner_width_1,
                disk_thickness,
                magnet_thickness,
                distance_between_stator_and_rotor):
    rotor_path = os.path.join(base_path, 'Rotor')
    if has_separate_master_files:
        _open_rotor_master(rotor_path)
    if hasattr(Gui, 'setActiveDocument') and hasattr(Gui, 'SendMsgToActiveView'):
        Gui.setActiveDocument(document.Name)
        Gui.SendMsgToActiveView('ViewFit')
    bottom_rotor = _assemble_bottom_rotor(
        document, rotor_path)
    document.recompute()
    App.setActiveDocument(document.Name)
    top_rotor = Draft.clone(bottom_rotor)
    top_rotor.Label = 'TopRotor'
    _position_top_rotor(top_rotor,
                        coil_inner_width_1,
                        disk_thickness,
                        magnet_thickness,
                        distance_between_stator_and_rotor)
    _move_bottom_rotor(bottom_rotor,
                       coil_inner_width_1,
                       disk_thickness,
                       magnet_thickness,
                       distance_between_stator_and_rotor)
    # H Shape
    # Draft.rotate(bottom_rotor, 35)
    return bottom_rotor, top_rotor


def _open_rotor_master(rotor_path):
    App.openDocument(os.path.join(rotor_path, 'Master.FCStd'))


def _assemble_bottom_rotor(document, rotor_path):
    rotor_resin_cast_label = 'RotorResinCast'
    rotor_disc1_label = 'Disc1'
    _merge_document(document, rotor_path, rotor_resin_cast_label)
    _merge_document(document, rotor_path, rotor_disc1_label)
    rotor = make_compound(document, 'BottomRotor', [
        find_object_by_label(document, rotor_resin_cast_label),
        find_object_by_label(document, rotor_disc1_label)
    ])
    return rotor


def _merge_document(document, rotor_path, name):
    document.mergeProject(
        os.path.join(rotor_path, name + '.FCStd'))
    enforce_recompute_last_spreadsheet(document)


def _move_bottom_rotor(rotor,
                       coil_inner_width_1,
                       disk_thickness,
                       magnet_thickness,
                       distance_between_stator_and_rotor):
    z = _calculate_rotor_z_offset(coil_inner_width_1,
                                  disk_thickness,
                                  magnet_thickness,
                                  distance_between_stator_and_rotor)
    Draft.move(rotor, App.Vector(0, 0, -z))


def _position_top_rotor(top_rotor,
                        coil_inner_width_1,
                        disk_thickness,
                        magnet_thickness,
                        distance_between_stator_and_rotor):
    App.DraftWorkingPlane.alignToPointAndAxis(
        App.Vector(0, 0, 0), App.Vector(0, 1, 0), 0)
    Draft.rotate(top_rotor, 180.0, App.Vector(0.0, 0.0, 0.0),
                 axis=App.Vector(0.0, 1.0, 0.0), copy=False)
    z = _calculate_rotor_z_offset(coil_inner_width_1,
                                  disk_thickness,
                                  magnet_thickness,
                                  distance_between_stator_and_rotor)
    Draft.move(top_rotor, App.Vector(0, 0, z))


def _calculate_rotor_z_offset(coil_inner_width_1,
                              disk_thickness,
                              magnet_thickness,
                              distance_between_stator_and_rotor):
    stator_thickness = coil_inner_width_1
    rotor_thickness = _calculate_rotor_thickness(
        disk_thickness, magnet_thickness)
    return (
        distance_between_stator_and_rotor +
        (stator_thickness / 2) +
        rotor_thickness
    )


def _calculate_rotor_thickness(disk_thickness, magnet_thickness):
    return disk_thickness + magnet_thickness
