"""Cross-document validation for the shared JSON contracts.

JSON Schema validates each document's shape. This module validates references
between the role, experience, and company-project documents before publication.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

JsonObject = Mapping[str, Any]


class ContractValidationError(ValueError):
    """Raised when shared contract documents cannot be safely published."""


def _records(value: Any, label: str, errors: list[str]) -> list[JsonObject]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        errors.append(f"{label} must be an array")
        return []

    records: list[JsonObject] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"{label}[{index}] must be an object")
            continue
        records.append(item)
    return records


def _index_unique(
    records: Iterable[JsonObject], label: str, errors: list[str]
) -> dict[str, JsonObject]:
    indexed: dict[str, JsonObject] = {}
    for index, record in enumerate(records):
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id:
            errors.append(f"{label}[{index}] has no valid id")
            continue
        if record_id in indexed:
            errors.append(f"duplicate {label} id: {record_id}")
            continue
        indexed[record_id] = record
    return indexed


def _string_ids(value: Any, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        errors.append(f"{label} must be an array")
        return []

    ids: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            errors.append(f"{label}[{index}] must be a non-empty string")
            continue
        ids.append(item)
    return ids


def _is_published(record: JsonObject | None) -> bool:
    return record is not None and record.get("status") == "published"


def validate_contract_links(
    role_catalog: JsonObject,
    experience_catalog: JsonObject,
    company_projects: Sequence[JsonObject],
) -> None:
    """Validate IDs and publication rules shared by all three contracts.

    Draft records may reference other draft records so the team can iterate.
    Published records may only depend on published records.
    """

    errors: list[str] = []

    roles = _index_unique(_records(role_catalog.get("roles"), "roles", errors), "role", errors)
    tracks: dict[str, JsonObject] = {}
    track_role: dict[str, str] = {}
    for role_id, role in roles.items():
        role_tracks = _records(role.get("tracks"), f"role {role_id}.tracks", errors)
        for track in role_tracks:
            track_id = track.get("id")
            if not isinstance(track_id, str) or not track_id:
                errors.append(f"role {role_id} has a track without a valid id")
                continue
            if track_id in tracks:
                errors.append(f"duplicate track id: {track_id}")
                continue
            tracks[track_id] = track
            track_role[track_id] = role_id

    categories = _index_unique(
        _records(experience_catalog.get("categories"), "categories", errors),
        "experience category",
        errors,
    )
    experiences = _index_unique(
        _records(experience_catalog.get("items"), "experience items", errors),
        "experience",
        errors,
    )

    for experience_id, experience in experiences.items():
        category_id = experience.get("categoryId")
        category = categories.get(category_id) if isinstance(category_id, str) else None
        if category is None:
            errors.append(f"experience {experience_id} references unknown category: {category_id}")

        role_ids = _string_ids(experience.get("roleIds"), f"experience {experience_id}.roleIds", errors)
        track_ids = _string_ids(
            experience.get("trackIds"), f"experience {experience_id}.trackIds", errors
        )

        for role_id in role_ids:
            if role_id not in roles:
                errors.append(f"experience {experience_id} references unknown role: {role_id}")
        for track_id in track_ids:
            if track_id not in tracks:
                errors.append(f"experience {experience_id} references unknown track: {track_id}")
            elif track_role[track_id] not in role_ids:
                errors.append(
                    f"experience {experience_id} track {track_id} does not belong to its roles"
                )

        if _is_published(experience):
            if not _is_published(category):
                errors.append(
                    f"published experience {experience_id} requires a published category"
                )
            for role_id in role_ids:
                if not _is_published(roles.get(role_id)):
                    errors.append(
                        f"published experience {experience_id} requires published role {role_id}"
                    )
            for track_id in track_ids:
                if not _is_published(tracks.get(track_id)):
                    errors.append(
                        f"published experience {experience_id} requires published track {track_id}"
                    )

    projects = _index_unique(company_projects, "company project", errors)
    for project_id, project in projects.items():
        role_id = project.get("roleId")
        role = roles.get(role_id) if isinstance(role_id, str) else None
        if role is None:
            errors.append(f"company project {project_id} references unknown role: {role_id}")

        track_ids = _string_ids(
            project.get("trackIds"), f"company project {project_id}.trackIds", errors
        )
        for track_id in track_ids:
            if track_id not in tracks:
                errors.append(f"company project {project_id} references unknown track: {track_id}")
            elif track_role[track_id] != role_id:
                errors.append(
                    f"company project {project_id} track {track_id} does not belong to role {role_id}"
                )

        entry_ids = _string_ids(
            project.get("entryExperienceIds"),
            f"company project {project_id}.entryExperienceIds",
            errors,
        )
        bridge_ids = _string_ids(
            project.get("bridgeExperienceIds"),
            f"company project {project_id}.bridgeExperienceIds",
            errors,
        )
        overlap = sorted(set(entry_ids) & set(bridge_ids))
        if overlap:
            errors.append(
                f"company project {project_id} repeats entry experiences as bridges: "
                + ", ".join(overlap)
            )

        referenced_experiences = entry_ids + bridge_ids
        for experience_id in referenced_experiences:
            if experience_id not in experiences:
                errors.append(
                    f"company project {project_id} references unknown experience: {experience_id}"
                )

        if _is_published(project):
            if not _is_published(role):
                errors.append(f"published company project {project_id} requires a published role")
            if not referenced_experiences:
                errors.append(
                    f"published company project {project_id} requires an entry or bridge experience"
                )
            evidence_ids = _string_ids(
                project.get("evidenceIds"),
                f"company project {project_id}.evidenceIds",
                errors,
            )
            if not evidence_ids:
                errors.append(f"published company project {project_id} requires evidence")
            for track_id in track_ids:
                if not _is_published(tracks.get(track_id)):
                    errors.append(
                        f"published company project {project_id} requires published track {track_id}"
                    )
            for experience_id in referenced_experiences:
                if not _is_published(experiences.get(experience_id)):
                    errors.append(
                        f"published company project {project_id} requires published experience "
                        f"{experience_id}"
                    )

    if errors:
        raise ContractValidationError("Invalid shared contracts:\n- " + "\n- ".join(errors))

