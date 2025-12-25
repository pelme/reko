import pytest
from django.core.exceptions import ValidationError

from .validators import SwishNumberValidator


class Test_SwishNumberValidator:
    @pytest.mark.parametrize(
        "value",
        [
            "0703083928",
            "0721044831",
            "0736692142",
            "0763243857",
            "1234567890",
        ],
    )
    def test_valid_value(self, value: str) -> None:
        assert SwishNumberValidator()(value) is None

    @pytest.mark.parametrize(
        "value",
        [
            "+46706083841",
            "+1234567890",
            "01234567890",
            "00706083841",
            "07060838412",
        ],
    )
    def test_invalid_value(self, value: str) -> None:
        with pytest.raises(ValidationError):
            SwishNumberValidator()(value)
