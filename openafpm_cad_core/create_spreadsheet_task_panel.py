"""
FreeCAD macro to create wind turbine document
with spreadsheet containing input parameters.
"""

from enum import Enum, unique
from typing import Any, Callable

import FreeCADGui as Gui
from PySide import QtGui

from .get_default_parameters import get_default_parameters

__all__ = ['CreateSpreadsheetTaskPanel']


@unique
class WindTurbine(Enum):
    T_SHAPE = 'T Shape'
    H_SHAPE = 'H Shape'
    STAR_SHAPE = 'Star Shape'


class CreateSpreadsheetTaskPanel:
    def __init__(self,
                 title: str,
                 on_close: Callable[[dict, dict, dict], Any] = None):
        self.form = QtGui.QWidget()
        self.form.setWindowTitle(title)
        self.on_close = on_close

        layout = QtGui.QVBoxLayout(self.form)

        # Row 1
        row1 = QtGui.QHBoxLayout()

        label = QtGui.QLabel('<strong>Variant:</strong>', self.form)
        self.combo_box = self.create_combo_box()

        row1.addWidget(label)
        row1.addWidget(self.combo_box)

        layout.addLayout(row1)

        # Row 2
        row2 = QtGui.QHBoxLayout()

        rotor_disk_radius_label = QtGui.QLabel(
            '<strong>Rotor Disk Radius:</strong>', self.form)
        self.rotor_disk_radius_value = self.create_rotor_disk_radius_value()

        row2.addWidget(rotor_disk_radius_label)
        row2.addWidget(self.rotor_disk_radius_value)

        layout.addLayout(row2)

    def create_rotor_disk_radius_value(self):
        default_variant = WindTurbine.T_SHAPE.value
        default_rotor_disk_radius = get_rotor_disk_radius(default_variant)
        return QtGui.QLabel(default_rotor_disk_radius, self.form)

    def create_combo_box(self):
        combo_box = QtGui.QComboBox(self.form)
        items = [variant.value for variant in list(WindTurbine)]
        combo_box.addItems(items)
        combo_box.activated[str].connect(self.handle_combo_box_activated)
        return combo_box

    def handle_combo_box_activated(self, selected_variant):
        selected_rotor_disk_radius = get_rotor_disk_radius(selected_variant)
        self.rotor_disk_radius_value.setText(selected_rotor_disk_radius)

    def accept(self):
        """
        Executed upon clicking "OK" button in FreeCAD Tasks panel.
        """
        variant = self.combo_box.currentText()
        parameters = get_default_parameters(variant)
        if self.on_close:
            self.on_close(parameters['magnafpm'],
                          parameters['furling'],
                          parameters['user'])
        Gui.Control.closeDialog()


def get_rotor_disk_radius(variant: str):
    parameters = get_default_parameters(variant)
    return str(parameters['magnafpm']['RotorDiskRadius'])
