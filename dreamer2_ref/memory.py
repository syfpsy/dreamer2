from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _state_dir(root: Path) -> Path:
    override = os.environ.get("DREAMER2_STATE_DIR")
    if override:
        return Path(override)
    return root / "state"


@dataclass(slots=True)
class MemoryOutcome:
    reply_lines: list[tuple[str, str]]
    events: list[dict[str, Any]]


def load_runtime_state(root: Path, profile: dict[str, Any]) -> dict[str, Any]:
    state_dir = _state_dir(root)
    state_dir.mkdir(parents=True, exist_ok=True)
    state_path = state_dir / "runtime_state.json"

    if state_path.exists():
        with state_path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
            return _normalize_runtime_state(loaded, profile)

    return _normalize_runtime_state(
        {
            "profileId": profile["profileId"],
            "modeId": "standby",
            "transmissionLog": [
                {"speaker": "shell", "text": "Companion presence initialized."},
                {"speaker": "shell", "text": "Pure-text tier active. Calm holds the field."},
            ],
            "durableMemories": [],
            "artifacts": [],
            "companions": ["entity.signal-bird"],
            "unlockedParts": {},
            "dreamDrafts": [],
            "surfaceFocus": "memory",
            "selectedMemoryId": None,
            "selectedArtifactId": None,
            "sessionCounter": 0,
        },
        profile,
    )


def _normalize_runtime_state(state: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(state)
    normalized.setdefault("profileId", profile["profileId"])
    normalized.setdefault("modeId", "standby")
    normalized.setdefault("transmissionLog", [])
    normalized.setdefault("durableMemories", [])
    normalized.setdefault("artifacts", [])
    normalized.setdefault("companions", ["entity.signal-bird"])
    normalized.setdefault("unlockedParts", {})
    normalized.setdefault("dreamDrafts", [])
    normalized.setdefault("surfaceFocus", "memory")
    normalized.setdefault("selectedMemoryId", None)
    normalized.setdefault("selectedArtifactId", None)
    normalized.setdefault("sessionCounter", 0)
    return normalized


def save_runtime_state(root: Path, state: dict[str, Any]) -> None:
    state_dir = _state_dir(root)
    state_dir.mkdir(parents=True, exist_ok=True)
    state_path = state_dir / "runtime_state.json"
    with state_path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)


def append_session_event(root: Path, actor: str, event_type: str, payload: dict[str, Any]) -> None:
    state_dir = _state_dir(root)
    state_dir.mkdir(parents=True, exist_ok=True)
    path = state_dir / "session_events.jsonl"
    record = {
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "actor": actor,
        "type": event_type,
        "payload": payload,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def derive_tags(text: str) -> set[str]:
    lowered = text.lower()
    tags: set[str] = set()

    if any(word in lowered for word in ("prefer", "always", "never", "remember", "ritual")):
        tags.add("preference")
    if any(word in lowered for word in ("goal", "build", "ship", "project")):
        tags.add("project.active")
    if any(word in lowered for word in ("repair", "recover", "fixed", "healed")):
        tags.add("recovery")
    if any(word in lowered for word in ("important", "milestone", "vow")):
        tags.add("relationship.marked")
    return tags


def remember_from_text(text: str, state: dict[str, Any]) -> MemoryOutcome:
    tags = derive_tags(text)

    if not tags:
        return MemoryOutcome(reply_lines=[], events=[])

    summary = summarize_text(text)
    for memory in state["durableMemories"]:
        if memory["summary"].lower() == summary.lower():
            return MemoryOutcome(
                reply_lines=[
                    ("memory", f"Continuity already holds: {summary}"),
                ],
                events=[],
            )

    memory_id = f"mem_{len(state['durableMemories']) + 1:04d}"
    category = _pick_category(tags)
    visibility = "symbolic" if {"preference", "relationship.marked", "recovery"} & tags else "inspectable"
    memory = {
        "id": memory_id,
        "category": category,
        "sourceSessionId": f"session_{state['sessionCounter']:04d}",
        "summary": summary,
        "body": text.strip(),
        "tags": sorted(tags),
        "salience": 0.88 if visibility == "symbolic" else 0.72,
        "retention": "durable",
        "disposition": "active",
        "visibility": visibility,
        "revisionCount": 0,
    }
    state["durableMemories"].append(memory)
    state["selectedMemoryId"] = memory_id

    reply_lines: list[tuple[str, str]] = [
        ("memory", f"Marked for continuity: {summary}"),
    ]
    events: list[dict[str, Any]] = []
    initial_artifact_count = len(state["artifacts"])

    created_events = _apply_tag_artifacts(state, memory_id, tags)
    for kind, line in created_events.messages:
        reply_lines.append((kind, line))
    events.extend(created_events.events)

    if len(state["artifacts"]) > initial_artifact_count:
        state["surfaceFocus"] = "gallery"
        state["selectedArtifactId"] = state["artifacts"][-1]["id"]
    else:
        state["surfaceFocus"] = "memory"
        state["selectedArtifactId"] = None
    return MemoryOutcome(reply_lines=reply_lines, events=events)


@dataclass(slots=True)
class _ArtifactApplication:
    messages: list[tuple[str, str]]
    events: list[dict[str, Any]]


def _apply_tag_artifacts(state: dict[str, Any], memory_id: str, tags: set[str]) -> _ArtifactApplication:
    messages: list[tuple[str, str]] = []
    events: list[dict[str, Any]] = []

    if "preference" in tags and not _has_artifact(state, "artifact.relic.archive-lantern"):
        state["artifacts"].append(
            {
                "id": f"artifact_{len(state['artifacts']) + 1:04d}",
                "type": "artifact.relic.archive-lantern",
                "title": "Archive Lantern",
                "sourceMemoryIds": [memory_id],
                "visualBinding": {"target": "relic", "partId": "relic.archive-lantern"},
                "displayRules": {
                    "visibility": "contextual",
                    "modes": ["standby", "listening", "dreaming", "focused"],
                },
                "stateEffects": [
                    "portrait:unlock-relic",
                    "ambient:quiet-orbit",
                    "gallery:add-card",
                    "companion:unlock-lantern-mote",
                ],
            }
        )
        state["unlockedParts"]["relic"] = "relic.archive-lantern"
        _ensure_companion(state, "entity.lantern-mote")
        messages.append(("shell", "Archive lantern kindled. The shell remembers visibly."))
        events.append(
            {
                "kind": "artifact-reveal",
                "presetId": "distortion.relic-phase",
                "durationSeconds": 1.2,
            }
        )

    if "recovery" in tags and not _has_artifact(state, "artifact.scar.stitched-echo"):
        state["artifacts"].append(
            {
                "id": f"artifact_{len(state['artifacts']) + 1:04d}",
                "type": "artifact.scar.stitched-echo",
                "title": "Stitched Echo",
                "sourceMemoryIds": [memory_id],
                "visualBinding": {"target": "scar", "partId": "scar.stitched-echo"},
                "displayRules": {
                    "visibility": "contextual",
                    "modes": ["recovering", "standby", "focused"],
                },
                "stateEffects": ["portrait:unlock-scar", "ambient:warm-quiet"],
            }
        )
        state["unlockedParts"]["scar"] = "scar.stitched-echo"
        messages.append(("shell", "A stitched mark remains. Recovery is now part of the face."))
        events.append(
            {
                "kind": "recovery-mark",
                "presetId": "distortion.relic-phase",
                "durationSeconds": 0.9,
            }
        )

    project_artifacts_created = False
    if "project.active" in tags and not _has_artifact(state, "artifact.timeline.marker"):
        _append_artifact(
            state,
            artifact_type="artifact.timeline.marker",
            title="Builder Mark",
            memory_id=memory_id,
            visual_target="gallery",
            part_id="artifact.timeline.marker",
            modes=["standby", "building", "focused"],
            state_effects=["gallery:add-tick", "shell:project-mark"],
        )
        project_artifacts_created = True

    if "project.active" in tags and not _has_artifact(state, "artifact.gallery.card"):
        _append_artifact(
            state,
            artifact_type="artifact.gallery.card",
            title="Workshop Snapshot",
            memory_id=memory_id,
            visual_target="gallery",
            part_id="artifact.gallery.card",
            modes=["standby", "building", "researching", "focused"],
            state_effects=["gallery:add-card", "companion:bind-archive-shard"],
        )
        project_artifacts_created = True

    if project_artifacts_created:
        messages.append(("shell", "A builder trace was pinned to the gallery spine."))
        events.append(
            {
                "kind": "artifact-reveal",
                "presetId": "distortion.breath",
                "durationSeconds": 0.55,
            }
        )

    if "relationship.marked" in tags and not _has_artifact(state, "artifact.orbit.fragment"):
        _append_artifact(
            state,
            artifact_type="artifact.orbit.fragment",
            title="Orbit Fragment",
            memory_id=memory_id,
            visual_target="ambient",
            part_id="artifact.orbit.fragment",
            modes=["standby", "listening", "dreaming", "focused"],
            state_effects=["ambient:orbit-fragment", "companion:bind-archive-shard"],
        )
        messages.append(("shell", "A small orbit fragment took position near the shell."))
        events.append(
            {
                "kind": "artifact-reveal",
                "presetId": "distortion.relic-phase",
                "durationSeconds": 0.8,
            }
        )

    return _ArtifactApplication(messages=messages, events=events)


def revise_memory(state: dict[str, Any], memory_id: str, new_text: str) -> MemoryOutcome:
    memory = next((item for item in state["durableMemories"] if item["id"] == memory_id), None)
    if memory is None:
        return MemoryOutcome(
            reply_lines=[("shell", f"No durable memory found for {memory_id}.")],
            events=[],
        )

    cleaned = new_text.strip()
    if not cleaned:
        return MemoryOutcome(
            reply_lines=[("shell", "Revise requires replacement text.")],
            events=[],
        )

    if cleaned.lower() == memory["body"].lower():
        return MemoryOutcome(
            reply_lines=[("memory", f"{memory_id} already holds that form.")],
            events=[],
        )

    previous_summary = memory["summary"]
    previous_tags = set(memory.get("tags", []))
    new_tags = derive_tags(cleaned)
    combined_tags = previous_tags | new_tags

    memory["summary"] = summarize_text(cleaned)
    memory["body"] = cleaned
    memory["tags"] = sorted(combined_tags)
    memory["category"] = _pick_category(combined_tags) if combined_tags else memory["category"]
    memory["revisionCount"] = int(memory.get("revisionCount", 0)) + 1
    state["selectedMemoryId"] = memory_id
    state["surfaceFocus"] = "memory"

    reply_lines: list[tuple[str, str]] = [
        ("memory", f"Revised {memory_id}: {memory['summary']}"),
    ]
    if previous_summary != memory["summary"]:
        reply_lines.append(("shell", f"Prior form released: {previous_summary}"))

    added_tags = new_tags - previous_tags
    events: list[dict[str, Any]] = [
        {
            "kind": "memory-resurfacing",
            "presetId": "distortion.relic-phase",
            "durationSeconds": 0.75,
        }
    ]

    if added_tags:
        application = _apply_tag_artifacts(state, memory_id, added_tags)
        for kind, line in application.messages:
            reply_lines.append((kind, line))
        events.extend(application.events)

    return MemoryOutcome(reply_lines=reply_lines, events=events)


def promote_dream_draft(state: dict[str, Any], draft_id: str | None = None) -> MemoryOutcome:
    if not state["dreamDrafts"]:
        return MemoryOutcome(
            reply_lines=[("shell", "No dream draft available to promote.")],
            events=[],
        )

    if draft_id:
        draft = next((item for item in state["dreamDrafts"] if item["id"] == draft_id), None)
        if draft is None:
            return MemoryOutcome(
                reply_lines=[("shell", f"No dream draft found for {draft_id}.")],
                events=[],
            )
    else:
        draft = state["dreamDrafts"][-1]

    summary_seed = draft["prompt"].strip() or _first_surface_line(draft)
    if not summary_seed:
        return MemoryOutcome(
            reply_lines=[("shell", f"Dream draft {draft['id']} has no promotable line.")],
            events=[],
        )

    body = "\n".join(draft["lines"])
    memory_id = f"mem_{len(state['durableMemories']) + 1:04d}"
    tags = {"dream.synthesis"} | derive_tags(summary_seed)

    memory = {
        "id": memory_id,
        "category": "relationship_narrative" if "relationship.marked" in tags else "long_term_personal",
        "sourceSessionId": f"session_{state['sessionCounter']:04d}",
        "summary": summarize_text(summary_seed),
        "body": body,
        "tags": sorted(tags),
        "salience": 0.82,
        "retention": "durable",
        "disposition": "active",
        "visibility": "symbolic",
        "revisionCount": 0,
        "promotedFromDraftId": draft["id"],
    }
    state["durableMemories"].append(memory)
    state["selectedMemoryId"] = memory_id

    reply_lines: list[tuple[str, str]] = [
        ("memory", f"Promoted dream draft {draft['id']} into {memory_id}."),
    ]
    events: list[dict[str, Any]] = [
        {
            "kind": "memory-resurfacing",
            "presetId": "distortion.relic-phase",
            "durationSeconds": 0.9,
        }
    ]

    synthesis_count = sum(1 for item in state["durableMemories"] if "dream.synthesis" in item.get("tags", []))
    if synthesis_count >= 2 and not _has_artifact(state, "artifact.orbit.fragment"):
        _append_artifact(
            state,
            artifact_type="artifact.orbit.fragment",
            title="Dream Shard",
            memory_id=memory_id,
            visual_target="ambient",
            part_id="artifact.orbit.fragment",
            modes=["standby", "listening", "dreaming", "focused"],
            state_effects=["ambient:orbit-fragment", "companion:bind-archive-shard", "dream:shard-formed"],
        )
        reply_lines.append(("shell", "Two dream syntheses held. A shard settled into orbit."))
        events.append(
            {
                "kind": "artifact-reveal",
                "presetId": "distortion.relic-phase",
                "durationSeconds": 0.85,
            }
        )
        state["surfaceFocus"] = "gallery"
        state["selectedArtifactId"] = state["artifacts"][-1]["id"]
    else:
        state["surfaceFocus"] = "memory"

    extra = _apply_tag_artifacts(state, memory_id, tags - {"dream.synthesis"})
    for kind, line in extra.messages:
        reply_lines.append((kind, line))
    events.extend(extra.events)

    return MemoryOutcome(reply_lines=reply_lines, events=events)


def inspect_memory_lines(memory: dict[str, Any], state: dict[str, Any]) -> list[tuple[str, str]]:
    tags = ", ".join(memory.get("tags", [])) or "none"
    linked = [
        artifact["id"]
        for artifact in state["artifacts"]
        if memory["id"] in artifact.get("sourceMemoryIds", [])
    ]
    lines: list[tuple[str, str]] = [
        ("memory", f"{memory['id']} {memory['summary']}"),
        ("shell", f"category {memory.get('category', 'unknown')} | visibility {memory.get('visibility', 'hidden')}"),
        ("shell", f"tags {tags}"),
        ("shell", f"source {memory.get('sourceSessionId', 'unknown')} | revisions {memory.get('revisionCount', 0)}"),
    ]
    if linked:
        lines.append(("shell", f"artifacts {', '.join(linked)}"))
    if memory.get("body") and memory["body"].strip() != memory["summary"].strip():
        lines.append(("memory", summarize_text(memory["body"], 140)))
    if memory.get("promotedFromDraftId"):
        lines.append(("shell", f"promoted from {memory['promotedFromDraftId']}"))
    return lines


def _first_surface_line(draft: dict[str, Any]) -> str:
    for line in draft.get("lines", []):
        if line.startswith("surface> "):
            return line[len("surface> ") :]
    for line in draft.get("lines", []):
        if line.startswith("focus> "):
            return line[len("focus> ") :]
    return ""


def forget_memory(state: dict[str, Any], memory_id: str) -> MemoryOutcome:
    memory = next((item for item in state["durableMemories"] if item["id"] == memory_id), None)
    if not memory:
        return MemoryOutcome(
            reply_lines=[("shell", f"No durable memory found for {memory_id}.")],
            events=[],
        )

    state["durableMemories"] = [item for item in state["durableMemories"] if item["id"] != memory_id]
    removed_artifacts = [artifact for artifact in state["artifacts"] if memory_id in artifact["sourceMemoryIds"]]
    state["artifacts"] = [artifact for artifact in state["artifacts"] if memory_id not in artifact["sourceMemoryIds"]]

    for artifact in removed_artifacts:
        _remove_artifact_visuals(state, artifact["type"])

    reply_lines: list[tuple[str, str]] = [
        ("memory", f"Forgotten {memory_id}: {memory['summary']}"),
    ]
    if removed_artifacts:
        reply_lines.append(("shell", "Visible marks tied only to that memory were released."))
    if not state["artifacts"]:
        state["surfaceFocus"] = "memory"
        state["selectedArtifactId"] = None
    elif any(artifact["id"] == state.get("selectedArtifactId") for artifact in removed_artifacts):
        state["selectedArtifactId"] = state["artifacts"][-1]["id"]

    if state["durableMemories"]:
        state["selectedMemoryId"] = state["durableMemories"][-1]["id"]
    else:
        state["selectedMemoryId"] = None

    return MemoryOutcome(
        reply_lines=reply_lines,
        events=[],
    )


def create_dream_draft(state: dict[str, Any], prompt: str) -> MemoryOutcome:
    draft_id = f"dream_{len(state['dreamDrafts']) + 1:04d}"
    recent_memories = state["durableMemories"][-3:]
    lines: list[str] = []

    if recent_memories:
        lines.append("Dream channel open. Reflective output remains draft.")
        for memory in recent_memories:
            lines.append(f"surface> {memory['summary']}")
    else:
        lines.append("Dream channel open. Nothing durable is deep enough to surface yet.")

    if any(artifact["type"] == "artifact.relic.archive-lantern" for artifact in state["artifacts"]):
        lines.append("The lantern circles what should not be dropped.")
    if prompt:
        lines.append(f"focus> {summarize_text(prompt, 58)}")

    state["dreamDrafts"].append(
        {
            "id": draft_id,
            "prompt": prompt,
            "lines": lines,
        }
    )
    state["dreamDrafts"] = state["dreamDrafts"][-6:]
    state["surfaceFocus"] = "dream"
    if recent_memories:
        state["selectedMemoryId"] = recent_memories[-1]["id"]

    return MemoryOutcome(
        reply_lines=[("shell", line) if index == 0 else ("memory", line) for index, line in enumerate(lines)],
        events=[
            {
                "kind": "dream-shift",
                "presetId": "distortion.dream-soft",
                "durationSeconds": 1.2,
            }
        ],
    )


def summarize_text(text: str, limit: int = 72) -> str:
    compact = " ".join(text.strip().split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _pick_category(tags: set[str]) -> str:
    if "preference" in tags:
        return "long_term_personal"
    if "relationship.marked" in tags:
        return "relationship_narrative"
    if "recovery" in tags:
        return "cosmetic_state"
    return "project_task"


def _has_artifact(state: dict[str, Any], artifact_type: str) -> bool:
    return any(artifact["type"] == artifact_type for artifact in state["artifacts"])


def _ensure_companion(state: dict[str, Any], companion_id: str) -> None:
    if companion_id not in state["companions"]:
        state["companions"].append(companion_id)


def _append_artifact(
    state: dict[str, Any],
    *,
    artifact_type: str,
    title: str,
    memory_id: str,
    visual_target: str,
    part_id: str,
    modes: list[str],
    state_effects: list[str],
) -> None:
    state["artifacts"].append(
        {
            "id": f"artifact_{len(state['artifacts']) + 1:04d}",
            "type": artifact_type,
            "title": title,
            "sourceMemoryIds": [memory_id],
            "visualBinding": {"target": visual_target, "partId": part_id},
            "displayRules": {
                "visibility": "contextual",
                "modes": list(modes),
            },
            "stateEffects": list(state_effects),
        }
    )


def _remove_artifact_visuals(state: dict[str, Any], artifact_type: str) -> None:
    if artifact_type == "artifact.relic.archive-lantern":
        if not _has_artifact(state, artifact_type):
            state["unlockedParts"].pop("relic", None)
            if "entity.lantern-mote" in state["companions"]:
                state["companions"].remove("entity.lantern-mote")
    if artifact_type == "artifact.scar.stitched-echo":
        if not _has_artifact(state, artifact_type):
            state["unlockedParts"].pop("scar", None)
