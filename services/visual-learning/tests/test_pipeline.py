from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest


PIPELINE_PATH = Path(__file__).resolve().parents[1]
if str(PIPELINE_PATH) not in sys.path:
    sys.path.insert(0, str(PIPELINE_PATH))

from pipeline import VisualLearningError, VisualLearningPipeline  # noqa: E402


def test_ingest_frame_normalizes_labels_and_time() -> None:
    observation = VisualLearningPipeline().ingest_frame(
        observation_id=" frame-001 ",
        source_id=" stream-a ",
        observed_at=datetime(2026, 5, 15, 13, 0, tzinfo=timezone.utc),
        modality="chart",
        width=1920,
        height=1080,
        frame_index=0,
        uri=" file:///frames/frame-001.png ",
        labels=["breakout", "breakout", " volume-spike "],
    )

    assert observation.observation_id == "frame-001"
    assert observation.source_id == "stream-a"
    assert observation.labels == ("breakout", "volume-spike")
    assert observation.observed_at.tzinfo == timezone.utc


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("observation_id", ""),
        ("source_id", ""),
        ("width", 0),
        ("height", -1),
        ("frame_index", -1),
        ("uri", ""),
    ],
)
def test_ingest_frame_rejects_invalid_values(field: str, value: object) -> None:
    payload = {
        "observation_id": "frame-001",
        "source_id": "stream-a",
        "observed_at": datetime(2026, 5, 15, 13, 0, tzinfo=timezone.utc),
        "modality": "video",
        "width": 1920,
        "height": 1080,
        "frame_index": 0,
        "uri": "file:///frames/frame-001.png",
    }
    payload[field] = value

    with pytest.raises(VisualLearningError):
        VisualLearningPipeline().ingest_frame(**payload)


def test_ingest_frame_requires_timezone() -> None:
    with pytest.raises(VisualLearningError):
        VisualLearningPipeline().ingest_frame(
            observation_id="frame-001",
            source_id="stream-a",
            observed_at=datetime(2026, 5, 15, 13, 0),
            modality="screen",
            width=1920,
            height=1080,
            frame_index=0,
            uri="file:///frames/frame-001.png",
        )
