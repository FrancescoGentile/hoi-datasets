##
##
##

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import NewType

from ._box import BoundingBox

# -----------------------------------------------------------------------------
# Sample
# -----------------------------------------------------------------------------

SampleID = NewType("SampleID", str)


@dataclass(frozen=True)
class Sample:
    """A sample in the dataset.

    Attributes
    ----------
    image_path : Path
        The path to the image file. This shold be an absolute path.
    entities : list[Entity]
        The entities present in the image.
    actions : list[Action]
        The actions occurring in the image.
    splits : list[str]
        The splits of the dataset that the sample belongs to.
    """

    image_path: Path
    entities: list[Entity]
    actions: list[Action]
    splits: list[str]


# -----------------------------------------------------------------------------
# Entity
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class Entity:
    """An entity in an image.

    Attributes
    ----------
    bbox : BoundingBox
        The bounding box of the entity.
    category : str
        The category of the entity. Note that different datasets may have different
        category names. The only requirement is that all and only human entities
        must be annotated with 'person'.
    """

    bbox: BoundingBox
    category: str


# -----------------------------------------------------------------------------
# Action
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class Action:
    """An action in an image.

    Attributes
    ----------
    verb : str
        The verb of the action. Note that different datasets may have different
        verb names.
    subject : int
        The index of the subject entity in the image.
    target : int | None
        The index of the target entity in the image. If the action is not a
        human-object or human-human interaction, this should be None.
    instrument : int | None
        The index of the instrument entity in the image. An instrument is an
        object that is used to perform the action but is not the target of the
        action. If the action does not involve an instrument, this should be None.
    """

    verb: str
    subject: int
    target: int | None
    instrument: int | None
