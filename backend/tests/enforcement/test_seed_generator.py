import pytest
from db.seed.generator import generate_rows


def test_generate_rows_is_deterministic_and_uses_requested_count() -> None:
    def make_row(random_source):
        return {"value": random_source.randrange(1000)}

    first = generate_rows(4, make_row, seed=23)
    second = generate_rows(4, make_row, seed=23)

    assert first == second
    assert len(first) == 4


def test_generate_zero_rows_does_not_call_the_factory() -> None:
    def fail_if_called(_random_source):
        raise AssertionError("factory should not be called")

    assert generate_rows(0, fail_if_called, seed=23) == []


@pytest.mark.parametrize("count", [-1, True, 1.5])
def test_generate_rows_rejects_invalid_counts(count) -> None:
    with pytest.raises(ValueError, match="non-negative integer"):
        generate_rows(count, lambda _random_source: {}, seed=23)


def test_generate_rows_requires_mapping_results() -> None:
    with pytest.raises(TypeError, match="return a mapping"):
        generate_rows(1, lambda _random_source: [], seed=23)
