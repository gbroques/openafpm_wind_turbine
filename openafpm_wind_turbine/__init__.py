import FreeCAD as App
import FreeCADGui as Gui
import Draft
from .master_of_puppets import create_master_of_puppets
import os
import importWebGL
from abc import ABC

# T Shape
# =======
# rotor_radius = 130
# rotor_inner_circle = 25
# hub_holes_placement = 44
# magnet_length = 46

# H Shape
# =======
# rotor_radius = 230
# rotor_inner_circle = 47.5
# hub_holes_placement = 78
# magnet_length = 46

# Star Shape
# ==========
rotor_radius = 349
rotor_inner_circle = 81.5
hub_holes_placement = 102.5
magnet_length = 58

magn_afpm_parameters = {
    'RotorDiskRadius': rotor_radius,
    'DiskThickness': 10,
    'MagnetLength': magnet_length,
    'MagnetWidth': 30,
    'MagnetThickness': 10,
    'NumberMagnet': 12,
    'StatorThickness': 13,
    'CoilLegWidth': 23.26,
    'CoilInnerWidth1': 30,
    'CoilInnerWidth2': 30
}

user_parameters = {
    # Distance of holes from center
    'HubHolesPlacement': hub_holes_placement,
    'RotorInnerCircle': rotor_inner_circle,
    'Holes': 7,
    'MetalLengthL': 80,
    'MetalThicknessL': 8,
    'FlatMetalThickness': 10,
    'YawPipeRadius': 58.15,
    'PipeThickness': 6,
    'ResineRotorMargin': 5,
    'HubHoles': 10
}


def main():
    master_of_puppets_doc_name = 'Master of Puppets'
    imported_spreadsheet_name = 'Spreadsheet001'
    master_spreadsheet_name = 'Spreadsheet'
    master_of_puppets_doc = create_master_of_puppets(
        master_of_puppets_doc_name,
        imported_spreadsheet_name,
        master_spreadsheet_name,
        magn_afpm_parameters,
        user_parameters)
    master_of_puppets_doc.recompute()

    wind_turbine = create_wind_turbine(magn_afpm_parameters)
    wind_turbine.render()


class WindTurbine(ABC):
    def __init__(self,
                 magn_afpm_parameters,
                 base_dir,
                 has_separate_master_files,
                 stator_resin_cast_name,
                 rotor_disc1_name):
        self.magn_afpm_parameters = magn_afpm_parameters
        self.has_separate_master_files = has_separate_master_files
        self.stator_resin_cast_name = stator_resin_cast_name
        self.rotor_resin_cast_name = 'PocketBody'
        self.rotor_disc1_name = rotor_disc1_name

        self.base_path = os.path.join(
            os.path.dirname(__file__), 'documents', base_dir)
        self.doc = App.newDocument('WindTurbine')

    def render(self):
        stator_path = os.path.join(self.base_path, 'Stator')
        if not self.has_separate_master_files:
            self._open_master()
        if self.has_separate_master_files:
            self._open_stator_master(stator_path)
        self._merge_stator_resin_cast(stator_path)

        rotor_path = os.path.join(self.base_path, 'Rotor')
        if self.has_separate_master_files:
            self._open_rotor_master(rotor_path)
        if hasattr(Gui, 'setActiveDocument') and hasattr(Gui, 'SendMsgToActiveView'):
            Gui.setActiveDocument(self.doc.Name)
            Gui.SendMsgToActiveView('ViewFit')
        rotor_name = 'Rotor'
        rotor = self._assemble_rotor(rotor_path, rotor_name)
        self.doc.recompute()
        App.setActiveDocument(self.doc.Name)
        top_rotor = Draft.clone(rotor)
        self._position_top_rotor(top_rotor)
        self._move_rotor(rotor)
        self._export_to_webgl(rotor_name)

    def _open_master(self):
        App.openDocument(os.path.join(
            self.base_path, 'MasterBigWindturbine.FCStd'))

    def _open_stator_master(self, stator_path):
        App.openDocument(os.path.join(stator_path, 'MasterStator.FCStd'))

    def _merge_stator_resin_cast(self, stator_path):
        self.doc.mergeProject(
            os.path.join(stator_path, 'StatorResinCast.FCStd'))
        self.doc.Spreadsheet.enforceRecompute()

    def _open_rotor_master(self, rotor_path):
        App.openDocument(os.path.join(rotor_path, 'Master.FCStd'))

    def _assemble_rotor(self, rotor_path, rotor_name):
        self._merge_rotor_resin_cast(rotor_path)
        self._merge_rotor_disc1(rotor_path)
        rotor = self.doc.addObject('Part::Compound', rotor_name)
        rotor.Links = [
            self.doc.getObject('PocketBody'),  # rotor_resin_cast_name
            self.doc.getObject(self.rotor_disc1_name)
        ]
        return rotor

    def _merge_rotor_resin_cast(self, rotor_path):
        self.doc.mergeProject(
            os.path.join(rotor_path, 'RotorResinCast.FCStd'))
        self._enforce_recompute_last_spreadsheet()

    def _merge_rotor_disc1(self, rotor_path):
        self.doc.mergeProject(
            os.path.join(rotor_path, 'Disc1.FCStd'))
        self._enforce_recompute_last_spreadsheet()

    def _enforce_recompute_last_spreadsheet(self):
        sheets = self.doc.findObjects('Spreadsheet::Sheet')
        last_sheet = sheets[len(sheets) - 1]
        last_sheet.enforceRecompute()

    def _move_rotor(self, rotor):
        placement = App.Placement()
        z = self._calculate_rotor_z_offset()
        placement.move(App.Vector(0, 0, -z))
        rotor.Placement = placement

    def _position_top_rotor(self, top_rotor):
        App.DraftWorkingPlane.alignToPointAndAxis(
            App.Vector(0, 0, 0), App.Vector(1, 0, 0), 0)
        Draft.rotate([top_rotor], 180.0, App.Vector(0.0, 0.0, 0.0),
                     axis=App.Vector(1.0, 0.0, 0.0), copy=False)
        z = self._calculate_rotor_z_offset()
        Draft.move(top_rotor, App.Vector(0, 0, z))

    def _calculate_rotor_z_offset(self):
        stator_thickness = magn_afpm_parameters['CoilInnerWidth1']
        distance_from_stator = 30
        rotor_thickness = self._calculate_rotor_thickness()
        return distance_from_stator + (stator_thickness / 2) + rotor_thickness

    def _calculate_rotor_thickness(self):
        return magn_afpm_parameters['DiskThickness'] + \
            magn_afpm_parameters['MagnetThickness']

    def _export_to_webgl(self, rotor_name):
        objects = [
            self.doc.getObject(self.stator_resin_cast_name),
            self.doc.getObject(rotor_name),
            self.doc.getObject('Clone') # Name of top rotor
        ]
        importWebGL.export(objects, 'wind-turbine-webgl.html')


class TShapeWindTurbine(WindTurbine):
    def __init__(self, magn_afpm_parameters):
        super().__init__(magn_afpm_parameters, 't_shape', True, 'Pad', 'Pocket001Body')


class HShapeWindTurbine(WindTurbine):
    def __init__(self, magn_afpm_parameters):
        super().__init__(magn_afpm_parameters, 'h_shape', True, 'Pad', 'Pocket001Body')


class StarShapeWindTurbine(WindTurbine):
    def __init__(self, magn_afpm_parameters):
        super().__init__(magn_afpm_parameters, 'star_shape', False, 'Body', 'Body001')


def create_wind_turbine(magn_afpm_parameters):
    rotor_radius = magn_afpm_parameters['RotorDiskRadius']
    if 0 <= rotor_radius < 187.5:
        return TShapeWindTurbine(magn_afpm_parameters)
    elif 187.5 <= rotor_radius <= 275:
        return HShapeWindTurbine(magn_afpm_parameters)
    else:
        return StarShapeWindTurbine(magn_afpm_parameters)