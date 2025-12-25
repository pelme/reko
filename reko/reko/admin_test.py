import pytest

from .admin import ProducerAdmin


class Test_ProducerAdmin:
    @pytest.mark.parametrize(
        ("value", "expected_is_valid"),
        [
            ("0703083928", True),
            ("1234567890", True),
            ("+46706083841", True),
            ("+1234567890", True),
            ("01234567890", False),
            ("00706083841", False),
            ("07060838412", False),
        ],
    )
    def test_ProducerForm(self, value: str, expected_is_valid: bool) -> None:
        form = ProducerAdmin.ProducerForm({"swish_number": value})
        assert form.is_valid() is expected_is_valid
