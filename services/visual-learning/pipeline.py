from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal


class VisualLearningError(ValueError):
    """Raised when visual-learning input cannot be trusted."""


@dataclass(frozen=True, slots=True)
class VisualObservation:
    observation_id: str
    source_id: str
    observed_at: datetime
    modality: Literal["chart", "video", "screen"]
    width: int
    height: int
    frame_index: int
    uri: str
    labels: tuple[str, ...]


class VisualLearningPipeline:
    def ingest_frame(
        self,
        *,
        observation_id: str,
        source_id: str,
        observed_at: datetime,
        modality: Literal["chart", "video", "screen"],
        width: int,
        height: int,
        frame_index: int,
        uri: str,
        labels: list[str] | tuple[str, ...] | None = None,
    ) -> VisualObservation:
        if not observation_id.strip():
            raise VisualLearningError("observation_id is required")
        if not source_id.strip():
            raise VisualLearningError("source_id is required")
        if width <= 0 or height <= 0:
            raise VisualLearningError("frame dimensions must be positive")
        if frame_index < 0:
            raise VisualLearningError("frame_index cannot be negative")
        if not uri.strip():
            raise VisualLearningError("uri is required")
        if observed_at.tzinfo is None:
            raise VisualLearningError("observed_at must be timezone-aware")

        normalized_labels = tuple(sorted({label.strip() for label in labels or () if label.strip()}))
        normalized_time = observed_at.astimezone(timezone.utc)

        return VisualObservation(
            observation_id=observation_id.strip(),
            source_id=source_id.strip(),
            observed_at=normalized_time,
            modality=modality,
            width=width,
            height=height,
            frame_index=frame_index,
            uri=uri.strip(),
            labels=normalized_labels,
        )
