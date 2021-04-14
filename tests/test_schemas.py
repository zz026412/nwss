from marshmallow import ValidationError
import pytest

from nwss import schemas


def test_valid_data(schema, valid_data):
    schema.load(valid_data)

def test_invalid_data(schema, invalid_data):
    with pytest.raises(ValidationError):
        schema.load(invalid_data)
