import csv
import os
import json
from contextlib import redirect_stdout
from io import StringIO

import pytest

from nwss.schemas import WaterSampleSchema
from nwss.dump_to_jsonschema import dump_schema


def load_data(infile):
    file_directory = os.path.dirname(__file__)
    absolute_file_directory = os.path.abspath(file_directory)

    with open(os.path.join(absolute_file_directory, infile), 'r') as f:
        data = [d for d in csv.DictReader(f)]

    return data


@pytest.fixture
def valid_data():
    return load_data('fixtures/valid_data.csv')


@pytest.fixture
def invalid_data():
    return load_data('fixtures/invalid_data.csv')


@pytest.fixture
def schema():
    return WaterSampleSchema(many=True)


@pytest.fixture
def json_schema():
<<<<<<< HEAD
    f = StringIO()
    with redirect_stdout(f):
        dump_schema()
    schema = f.getvalue()
    return json.loads(schema)
=======
    with open('schema.json', 'r') as f:
        return json.load(f)
>>>>>>> add jsonschema


@pytest.fixture
def valid_json():
    file_directory = os.path.dirname(__file__)
    absolute_file_directory = os.path.abspath(file_directory)
    file_name = os.path.join(absolute_file_directory, 'fixtures/valid.json')

    with open(file_name, 'r') as f:
        return json.load(f)
