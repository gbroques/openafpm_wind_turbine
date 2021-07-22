import sys
from typing import Callable, Optional

from FreeCAD import Console, Document


def _with_error_exit(find_object_by_label: Callable[[str], object]) -> Callable[[str], object]:
    def wrapped(document, label):
        result = find_object_by_label(document, label)
        if result is None:
            Console.PrintError(
                'No object with Label "{}" found in document. Check {}.FCStd.'.format(label, label))
            sys.exit(1)
        return result
    return wrapped


@_with_error_exit
def find_object_by_label(document: Document, label: str) -> Optional[object]:
    objects = document.getObjectsByLabel(label)
    if len(objects) == 0:
        return None
    return objects[0]
