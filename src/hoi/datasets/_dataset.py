##
##
##

from typing import Iterator, Protocol

from hoi.structs import Sample, SampleID


class Dataset(Protocol):
    """An interface for all datasets."""

    @property
    def categories(self) -> list[str]:
        """The categories of entities in the dataset."""
        ...

    @property
    def verbs(self) -> list[str]:
        """The verbs in the dataset."""
        ...

    @property
    def splits(self) -> list[str]:
        """The splits of the dataset."""
        ...

    def __len__(self) -> int:
        """The number of samples in the dataset."""
        ...

    def __iter__(self) -> Iterator[tuple[SampleID, Sample]]:
        """Iterates over all samples in the dataset."""
        ...

    def __getitem__(self, id: SampleID) -> Sample:
        """Gets the sample with the given ID."""
        ...
