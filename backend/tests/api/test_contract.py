"""Contract model coverage for API v0.1."""

from app.schemas import ChatResponse
from tests.api.contract_fixtures import PRESENTATIONS, STATUSES, contract_response_fixtures


def test_contract_fixtures_cover_each_status_and_presentation() -> None:
    fixtures = contract_response_fixtures()
    assert len(fixtures) == len(STATUSES) * len(PRESENTATIONS)

    for fixture in fixtures.values():
        response = ChatResponse.model_validate(fixture)
        assert ChatResponse.model_validate_json(response.model_dump_json()) == response


def test_answered_response_requires_evidence() -> None:
    fixture = contract_response_fixtures()["answered__text"]
    fixture["evidence"] = []

    try:
        ChatResponse.model_validate(fixture)
    except ValueError as error:
        assert "require evidence" in str(error)
    else:
        raise AssertionError("answered response without evidence must not validate")
