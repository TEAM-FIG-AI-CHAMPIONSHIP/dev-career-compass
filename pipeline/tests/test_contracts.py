import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

from career_compass_pipeline.contracts import ContractValidationError, validate_contract_links

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "packages" / "contracts" / "schemas"
EXAMPLES = ROOT / "packages" / "contracts" / "examples"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def load_example(name: str) -> dict:
    return load_json(EXAMPLES / name)


@pytest.fixture
def contracts() -> tuple[dict, dict, list[dict]]:
    return (
        load_example("role-catalog.example.json"),
        load_example("experience-catalog.example.json"),
        [load_example("company-project.example.json")],
    )


@pytest.mark.parametrize(
    ("schema_name", "example_name"),
    [
        ("role-catalog.schema.json", "role-catalog.example.json"),
        ("experience-catalog.schema.json", "experience-catalog.example.json"),
        ("company-project.schema.json", "company-project.example.json"),
    ],
)
def test_examples_match_json_schema(schema_name: str, example_name: str) -> None:
    schema = load_json(SCHEMAS / schema_name)
    example = load_example(example_name)
    Draft7Validator.check_schema(schema)
    errors = sorted(Draft7Validator(schema).iter_errors(example), key=lambda error: error.json_path)

    assert not errors, "\n".join(error.message for error in errors)


def test_example_contracts_have_valid_links(contracts: tuple[dict, dict, list[dict]]) -> None:
    validate_contract_links(*contracts)


def test_duplicate_track_ids_are_rejected(contracts: tuple[dict, dict, list[dict]]) -> None:
    roles, experiences, projects = deepcopy(contracts)
    duplicate = deepcopy(roles["roles"][0]["tracks"][0])
    roles["roles"][0]["tracks"].append(duplicate)

    with pytest.raises(ContractValidationError, match="duplicate track id"):
        validate_contract_links(roles, experiences, projects)


def test_experience_track_must_belong_to_one_of_its_roles(
    contracts: tuple[dict, dict, list[dict]],
) -> None:
    roles, experiences, projects = deepcopy(contracts)
    roles["roles"].append(
        {
            "id": "frontend",
            "label": "웹 프론트엔드",
            "status": "draft",
            "tracks": [{"id": "service-ui", "label": "서비스 UI", "status": "draft"}],
        }
    )
    experiences["items"][0]["trackIds"] = ["service-ui"]

    with pytest.raises(ContractValidationError, match="does not belong to its roles"):
        validate_contract_links(roles, experiences, projects)


def test_published_experience_requires_published_dependencies(
    contracts: tuple[dict, dict, list[dict]],
) -> None:
    roles, experiences, projects = deepcopy(contracts)
    experiences["items"][0]["status"] = "published"

    with pytest.raises(ContractValidationError, match="requires a published category"):
        validate_contract_links(roles, experiences, projects)


def test_project_entry_and_bridge_experiences_cannot_overlap(
    contracts: tuple[dict, dict, list[dict]],
) -> None:
    roles, experiences, projects = deepcopy(contracts)
    projects[0]["bridgeExperienceIds"] = ["rest-api-design"]

    with pytest.raises(ContractValidationError, match="repeats entry experiences as bridges"):
        validate_contract_links(roles, experiences, projects)


def test_published_project_requires_published_references(
    contracts: tuple[dict, dict, list[dict]],
) -> None:
    roles, experiences, projects = deepcopy(contracts)
    projects[0]["status"] = "published"

    with pytest.raises(ContractValidationError, match="requires published track"):
        validate_contract_links(roles, experiences, projects)


def company_project_validator() -> Draft7Validator:
    return Draft7Validator(load_json(SCHEMAS / "company-project.schema.json"))


def test_draft_company_project_may_omit_steps() -> None:
    """다듬는 중인 문서는 할 일이 비어 있어도 된다."""
    project = deepcopy(load_example("company-project.example.json"))
    project["status"] = "draft"
    project.pop("steps")

    assert not list(company_project_validator().iter_errors(project))


def test_published_company_project_requires_steps() -> None:
    """게시된 문서는 실행할 수 있어야 한다 — 요약 문단만으로는 화면이 할 일을 만들지 못한다."""
    project = deepcopy(load_example("company-project.example.json"))
    project["status"] = "published"

    without_steps = deepcopy(project)
    without_steps.pop("steps")
    assert list(company_project_validator().iter_errors(without_steps))

    empty_steps = deepcopy(project)
    empty_steps["steps"] = []
    assert list(company_project_validator().iter_errors(empty_steps))
