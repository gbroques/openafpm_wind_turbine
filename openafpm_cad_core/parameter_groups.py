
"""Module containing parameter group definitions.
"""

from typing import TypedDict

__all__ = [
    'MagnafpmParameters',
    'UserParameters',
    'FurlingParameters'
]

class MagnafpmParameters(TypedDict):
    """Parameters from the MagnAFPM tool."""
    
    RotorDiskRadius: float
    """Radius of rotor disk."""
    
    DiskThickness: float
    MagnetLength: float
    MagnetWidth: float
    MagnetThickness: float
    NumberMagnet: int
    StatorThickness: float
    CoilLegWidth: float
    CoilInnerWidth1: float
    CoilInnerWidth2: float
    MechanicalClearance: float


class UserParameters(TypedDict):
    """User Parameters."""

    HubHolesPlacement: float
    RotorInnerCircle: float
    Holes: float
    MetalLengthL: float
    MetalThicknessL: float
    FlatMetalThickness: float
    YawPipeRadius: float
    PipeThickness: float
    ResineRotorMargin: float
    HubHoles: float
    HorizontalPlaneAngle: float


class FurlingParameters(TypedDict):
    """Furling Parameters."""
    VerticalPlaneAngle: float
    BracketLength: float
    BracketWidth: float
    BracketThickness: float
    BoomLength: float
    BoomPipeRadius: float
    BoomPipeThickness: float
    VaneThickness: float
    VaneLength: float
    VaneWidth: float
    Offset: float
