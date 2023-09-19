##
##
##

import enum
from dataclasses import dataclass
from typing import Self, assert_never


class BoundingBoxFormat(enum.Enum):
    """The format of a bounding box."""

    XYXY = "xyxy"
    XYWH = "xywh"
    CXCYWH = "cxcywh"

    @classmethod
    def from_str(cls, s: str) -> Self:
        return cls[s.upper().strip()]

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class BoundingBox:
    """A bounding box.

    Attributes
    ----------
    coordinates : tuple[float, float, float, float]
        The coordinates of the bounding box. The coordinates are in the format
        specified by `format`.
    format : BoundingBoxFormat
        The format of the coordinates.
    normalized : bool
        Whether the coordinates are normalized. If True, the coordinates are
        normalized to the range [0, 1]. Otherwise, the coordinates are in pixels.
    """

    coordinates: tuple[float, float, float, float]
    format: BoundingBoxFormat
    normalized: bool

    def __post_init__(self) -> None:
        if len(self.coordinates) != 4:
            raise ValueError(f"Expected 4 coordinates, got {len(self.coordinates)}.")

    def normalize(self, size: tuple[int, int]) -> Self:
        """Normalizes the bounding box coordinates to the range [0, 1].

        Parameters
        ----------
        size : tuple[int, int]
            The size of the image that the bounding box is in. The size should be
            in the format (width, height).

        Returns
        -------
        BoundingBox
            The bounding box with normalized coordinates.
        """

        if self.normalized:
            return self

        w, h = size
        return self.__class__(
            coordinates=(
                self.coordinates[0] / w,
                self.coordinates[1] / h,
                self.coordinates[2] / w,
                self.coordinates[3] / h,
            ),
            format=self.format,
            normalized=True,
        )

    def denormalize(self, size: tuple[int, int]) -> Self:
        """Denormalizes the bounding box coordinates to the pixel range.

        Parameters
        ----------
        size : tuple[int, int]
            The size of the image that the bounding box is in. The size should be
            in the format (width, height).

        Returns
        -------
        BoundingBox
            The bounding box with denormalized coordinates.
        """

        if not self.normalized:
            return self

        w, h = size
        return self.__class__(
            coordinates=(
                self.coordinates[0] * w,
                self.coordinates[1] * h,
                self.coordinates[2] * w,
                self.coordinates[3] * h,
            ),
            format=self.format,
            normalized=False,
        )

    def to_xyxy(self) -> Self:
        """Converts the bounding box to the xyxy format.

        Returns
        -------
        BoundingBox
            The bounding box in the xyxy format.
        """

        match self.format:
            case BoundingBoxFormat.XYXY:
                return self
            case BoundingBoxFormat.XYWH:
                xmin, ymin, w, h = self.coordinates
                return self.__class__(
                    coordinates=(xmin, ymin, xmin + w, ymin + h),
                    format=BoundingBoxFormat.XYXY,
                    normalized=self.normalized,
                )
            case BoundingBoxFormat.CXCYWH:
                cx, cy, w, h = self.coordinates
                return self.__class__(
                    coordinates=(
                        cx - w / 2,
                        cy - h / 2,
                        cx + w / 2,
                        cy + h / 2,
                    ),
                    format=BoundingBoxFormat.XYXY,
                    normalized=self.normalized,
                )
            case _ as e:
                assert_never(e)

    def to_xywh(self) -> Self:
        """Converts the bounding box to the xywh format.

        Returns
        -------
        BoundingBox
            The bounding box in the xywh format.
        """

        match self.format:
            case BoundingBoxFormat.XYWH:
                return self
            case BoundingBoxFormat.XYXY:
                xmin, ymin, xmax, ymax = self.coordinates
                return self.__class__(
                    coordinates=(xmin, ymin, xmax - xmin, ymax - ymin),
                    format=BoundingBoxFormat.XYWH,
                    normalized=self.normalized,
                )
            case BoundingBoxFormat.CXCYWH:
                cx, cy, w, h = self.coordinates
                return self.__class__(
                    coordinates=(
                        cx - w / 2,
                        cy - h / 2,
                        w,
                        h,
                    ),
                    format=BoundingBoxFormat.XYWH,
                    normalized=self.normalized,
                )
            case _ as e:
                assert_never(e)

    def to_cxcywh(self) -> Self:
        """Converts the bounding box to the cxcywh format.

        Returns
        -------
        BoundingBox
            The bounding box in the cxcywh format.
        """

        match self.format:
            case BoundingBoxFormat.CXCYWH:
                return self
            case BoundingBoxFormat.XYXY:
                xmin, ymin, xmax, ymax = self.coordinates
                return self.__class__(
                    coordinates=(
                        (xmin + xmax) / 2,
                        (ymin + ymax) / 2,
                        xmax - xmin,
                        ymax - ymin,
                    ),
                    format=BoundingBoxFormat.CXCYWH,
                    normalized=self.normalized,
                )
            case BoundingBoxFormat.XYWH:
                xmin, ymin, w, h = self.coordinates
                return self.__class__(
                    coordinates=(
                        xmin + w / 2,
                        ymin + h / 2,
                        w,
                        h,
                    ),
                    format=BoundingBoxFormat.CXCYWH,
                    normalized=self.normalized,
                )
            case _ as e:
                assert_never(e)

    def convert(self, format: BoundingBoxFormat) -> Self:
        """Converts the bounding box to the specified format.

        Parameters
        ----------
        format : BoundingBoxFormat
            The format to convert the bounding box to.

        Returns
        -------
        BoundingBox
            The bounding box in the specified format.
        """

        match format:
            case BoundingBoxFormat.XYXY:
                return self.to_xyxy()
            case BoundingBoxFormat.XYWH:
                return self.to_xywh()
            case BoundingBoxFormat.CXCYWH:
                return self.to_cxcywh()
            case _ as e:
                assert_never(e)
