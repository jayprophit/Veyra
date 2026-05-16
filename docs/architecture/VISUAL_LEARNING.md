# Visual Learning

## Purpose

Visual learning lets Veyra ingest charts, dashboards, videos, screen captures, and other time-based visual evidence as research inputs. It is not permission for a model to trade from unverified images.

## Build Order

1. Define observation contracts and provenance.
2. Ingest frames and clips with timestamps, source IDs, and labels.
3. Build annotation and evaluation datasets.
4. Add open-source vision encoders and OCR.
5. Compare visual signals against structured market data.
6. Only then experiment with multimodal forecasting models.

## Required Controls

- consent and licensing for every video source
- immutable source IDs and timestamps
- separation between observation, interpretation, and action
- human review for model-generated labels
- backtests against structured baselines
- audit logs for any visual signal used downstream

## Initial Implementation

The starter implementation in `services/visual-learning` validates incoming frame metadata and creates deterministic `VisualObservation` records. It does not yet download videos, run OCR, train models, or place trades.
