##
##
##

import json
from pathlib import Path
from typing import Iterator

from hoi.structs import Action, BoundingBox, BoundingBoxFormat, Entity, Sample, SampleID

from ._dataset import Dataset


class H2ODataset(Dataset):
    """The Human-to-Human-or-Object Interaction Dataset."""

    def __init__(self, path: Path | str) -> None:
        """Initializes a new H20Dataset instance.

        Parameters
        ----------
        path : Path | str
            The path to the folder containing the dataset.
        """

        super().__init__()

        self._path = Path(path)

        self._categories = self._get_categories()
        self._verbs = self._get_verbs()

        self._samples = {
            id: sample
            for split in self.splits
            for id, sample in self._get_samples(split)
        }

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    @property
    def categories(self) -> list[str]:
        return self._categories

    @property
    def verbs(self) -> list[str]:
        return self._verbs

    @property
    def splits(self) -> list[str]:
        return ["train", "test"]

    def __len__(self) -> int:
        return len(self._samples)

    def __iter__(self) -> Iterator[tuple[SampleID, Sample]]:
        return iter(self._samples.items())

    def __getitem__(self, id: SampleID) -> Sample:
        return self._samples[id]

    # -------------------------------------------------------------------------
    # Private API
    # -------------------------------------------------------------------------

    def _get_categories(self) -> list[str]:
        """Returns the list of categories in the dataset.

        Returns
        -------
        list[str]
            The list of categories in the dataset.
        """

        with (self._path / "categories.json").open("r") as f:
            return json.load(f)

    def _get_verbs(self) -> list[str]:
        """Returns the list of verbs in the dataset.

        Returns
        -------
        list[str]
            The list of verbs in the dataset.
        """

        with (self._path / "verbs.json").open("r") as f:
            return json.load(f)

    def _get_samples(self, split: str) -> list[tuple[SampleID, Sample]]:
        """Returns the list of samples in the dataset.

        Parameters
        ----------
        split : str
            The split to get the samples for.

        Returns
        -------
        list[tuple[SampleID, Sample]]
            The list of samples in the dataset.
        """

        with (self._path / f"{split}.json").open("r") as f:
            data = json.load(f)

        samples = []
        for sample_data in data:
            id = SampleID(sample_data["id"])
            image = self._path / "images" / f"{split}" / f"{id}.jpg"

            entities = []
            for entity_data in sample_data["entities"]:
                entities.append(
                    Entity(
                        bbox=BoundingBox(
                            entity_data["bbox"], BoundingBoxFormat.XYXY, True
                        ),
                        category=entity_data["category"],
                    )
                )

            actions = []
            for action_data in sample_data["actions"]:
                actions.append(
                    Action(
                        verb=action_data["verb"],
                        subject=action_data["subject"],
                        target=action_data["target"],
                        instrument=action_data["instrument"],
                    )
                )

            sample = Sample(
                image_path=image, entities=entities, actions=actions, splits=[split]
            )
            samples.append((id, sample))

        return samples
