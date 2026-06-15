from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "contracts/video_temporal_policy.json"
FRAME_STREAM = ROOT / "data/frame_stream.csv"
OUTPUT = ROOT / "output"


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def read_frames() -> list[dict]:
    with FRAME_STREAM.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["t_s"] = float(row["t_s"])
        row["objects_list"] = [item.strip().lower() for item in row["objects"].split(";") if item.strip()]
        row["search_blob"] = " ".join(
            [
                row.get("caption", ""),
                row.get("ocr", ""),
                row.get("transcript", ""),
                row.get("objects", ""),
            ]
        ).lower()
    return rows


def rule_matches(frame: dict, rule: dict) -> bool:
    ocr = frame.get("ocr", "").lower()
    caption = frame.get("caption", "").lower()
    objects = set(frame.get("objects_list", []))

    checks = []
    checks.extend(term.lower() in ocr for term in rule.get("match_any_ocr", []))
    checks.extend(term.lower() in caption for term in rule.get("match_any_caption", []))
    checks.extend(term.lower() in objects for term in rule.get("match_any_objects", []))
    return any(checks)


def build_events(frames: list[dict], rules: list[dict], max_merge_gap_s: float) -> list[dict]:
    raw_events = []
    for frame in frames:
        for rule in rules:
            if rule_matches(frame, rule):
                window = float(rule.get("default_window_s", 2.0))
                raw_events.append(
                    {
                        "video_id": frame["video_id"],
                        "event_id": rule["event_id"],
                        "label": rule["label"],
                        "start_s": round(max(0.0, frame["t_s"] - window / 2), 3),
                        "end_s": round(frame["t_s"] + window / 2, 3),
                        "evidence_frame_ids": [frame["frame_id"]],
                        "evidence_modalities": rule.get("modalities", ["frame"]),
                        "evidence": [
                            {
                                "frame_id": frame["frame_id"],
                                "t_s": frame["t_s"],
                                "caption": frame.get("caption", ""),
                                "ocr": frame.get("ocr", ""),
                                "objects": frame.get("objects_list", []),
                                "transcript": frame.get("transcript", ""),
                            }
                        ],
                    }
                )

    raw_events.sort(key=lambda item: (item["video_id"], item["event_id"], item["start_s"]))
    merged = []
    for event in raw_events:
        previous = merged[-1] if merged else None
        if (
            previous
            and previous["video_id"] == event["video_id"]
            and previous["event_id"] == event["event_id"]
            and event["start_s"] - previous["end_s"] <= max_merge_gap_s
        ):
            previous["end_s"] = max(previous["end_s"], event["end_s"])
            previous["evidence_frame_ids"].extend(event["evidence_frame_ids"])
            previous["evidence"].extend(event["evidence"])
            previous["evidence_modalities"] = sorted(set(previous["evidence_modalities"]) | set(event["evidence_modalities"]))
        else:
            merged.append(event)
    return merged


def write_temporal_index(events: list[dict], frames: list[dict], policy: dict) -> None:
    OUTPUT.mkdir(exist_ok=True)
    index = {
        "schema_version": "1.0",
        "project": "IA para gente curiosa",
        "fasciculo": 12,
        "capitulo": 8,
        "source": "data/frame_stream.csv",
        "sampling": policy["sampling"],
        "event_count": len(events),
        "events": events,
    }
    (OUTPUT / "temporal_index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

    with (OUTPUT / "temporal_index.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "video_id",
                "event_id",
                "label",
                "start_s",
                "end_s",
                "evidence_frame_ids",
                "evidence_modalities",
            ],
        )
        writer.writeheader()
        for event in events:
            writer.writerow(
                {
                    "video_id": event["video_id"],
                    "event_id": event["event_id"],
                    "label": event["label"],
                    "start_s": event["start_s"],
                    "end_s": event["end_s"],
                    "evidence_frame_ids": "|".join(event["evidence_frame_ids"]),
                    "evidence_modalities": "|".join(event["evidence_modalities"]),
                }
            )

    videos = {}
    for frame in frames:
        item = videos.setdefault(frame["video_id"], {"frame_count": 0, "max_t_s": 0.0})
        item["frame_count"] += 1
        item["max_t_s"] = max(item["max_t_s"], frame["t_s"])

    clip_seconds = float(policy["sampling"]["default_clip_seconds"])
    stride_seconds = float(policy["sampling"]["default_stride_seconds"])
    with (OUTPUT / "capacity_estimate.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "video_id",
                "observed_duration_s",
                "observed_frames",
                "observed_fps",
                "frames_per_hour_at_observed_rate",
                "clips_per_hour_at_default_stride",
            ],
        )
        writer.writeheader()
        for video_id, item in sorted(videos.items()):
            duration = max(item["max_t_s"], 1.0)
            observed_fps = item["frame_count"] / duration
            clips_per_hour = math.floor(max(0.0, 3600.0 - clip_seconds) / stride_seconds) + 1
            writer.writerow(
                {
                    "video_id": video_id,
                    "observed_duration_s": round(duration, 3),
                    "observed_frames": item["frame_count"],
                    "observed_fps": round(observed_fps, 4),
                    "frames_per_hour_at_observed_rate": round(3600.0 * observed_fps, 2),
                    "clips_per_hour_at_default_stride": clips_per_hour,
                }
            )

    manifest = {
        "pipeline": [
            "ingesta_video",
            "extraccion_frames_audio_ocr",
            "frame_stream_csv",
            "reglas_eventos",
            "temporal_index",
            "auditoria_respuesta",
        ],
        "engineering_checks": [
            "versionar politica de muestreo",
            "guardar modalidad de evidencia",
            "bloquear texto visual no confiable",
            "medir capacidad por hora de video",
            "exigir answer/review/block",
        ],
    }
    (OUTPUT / "video_pipeline_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    policy = load_policy()
    frames = read_frames()
    events = build_events(
        frames=frames,
        rules=policy["event_extraction"]["rules"],
        max_merge_gap_s=float(policy["event_extraction"]["max_merge_gap_s"]),
    )
    write_temporal_index(events, frames, policy)
    print(f"OK: índice temporal generado con {len(events)} eventos en {OUTPUT}")


if __name__ == "__main__":
    main()
