from pathlib import Path

import FreeCAD as App

from .create_spreadsheet_document import create_spreadsheet_document
from .gui_document import get_gui_document_by_path, write_gui_documents
from .parameter_groups import (FurlingParameters, MagnafpmParameters,
                               UserParameters)
from .wind_turbine import WindTurbine

__all__ = ['load_turbine']


def load_turbine(magnafpm_parameters: MagnafpmParameters,
                 furling_parameters: FurlingParameters,
                 user_parameters: UserParameters) -> WindTurbine:
    spreadsheet_document = create_spreadsheet_document(
        magnafpm_parameters, furling_parameters, user_parameters)
    package_path = Path(__file__).parent.absolute()
    documents_path = package_path.joinpath('documents')
    gui_document_by_path = get_gui_document_by_path(documents_path)
    spreadsheet_document_path = documents_path.joinpath(
        'Master of Puppets.FCStd')
    # TODO: Mutates filesystem
    spreadsheet_document.saveAs(str(spreadsheet_document_path))
    root_document_path = documents_path.joinpath('WindTurbine.FCStd')
    root_document = App.openDocument(str(root_document_path))
    for obj in spreadsheet_document.Objects:
        obj.recompute()
    spreadsheet_document.recompute(None, True, True)
    sort_in_dependency_order = True
    document_by_name = App.listDocuments(sort_in_dependency_order)
    documents = document_by_name.values()
    for document in documents:
        for obj in document.Objects:
            obj.recompute()
        document.recompute(None, True, True)
        # TODO: Mutates filesystem
        document.save()
    # TODO: Mutates filesystem
    write_gui_documents(gui_document_by_path)
    return WindTurbine(root_document)
