import json
from pathlib import Path
from typing import TypedDict

from .parameter_groups import (FurlingParameters, MagnafpmParameters,
                               UserParameters)


class Parameters(TypedDict):
    magnafpm: MagnafpmParameters
    user: UserParameters
    furling: FurlingParameters

__all__ = ['get_default_parameters']


def get_default_parameters(variant: str) -> Parameters:
    """
    Variant must be one of "T Shape", "H Shape", or "Star Shape".
    """
    dir_path = Path(__file__).parent.resolve()
    parameters_path = dir_path.joinpath('parameters.json')

    with open(parameters_path) as f:
        parameters_by_variant = json.load(f)
    return parameters_by_variant[variant]
