# 💧 nwss-data-standard

A marshmallow schema for the National Wastewater Surveillance System

## Usage

### Installation

```bash
# Install from GitHub
pip install git+https://github.com/datamade/nwss-data-standard.git

# Install local copy
git clone https://github.com/datamade/nwss-data-standard.git && cd nwss-data-standard
pip install .
```

### Demo

Go to XXX to validate a CSV file against the standard

### Python

```python
from marshmallow import ValidationError
from nwss.schemas import WaterSampleSchema

sample_data = [
    # array of dictionaries
]

schema = WaterSampleSchema(many=True)

try:
    schema.load(sample_data)
except ValidationError as e:
    print(e.messages)
```

### JavaScript

tktk

## Development

### Schema

Install the app locally.

```python
git clone https://github.com/datamade/nwss-data-standard.git && cd nwss-data-standard
pip install -e .[dev]
```

Make your changes, then run the tests.

```python 
pytest
```

### JSON Schema
If you make any changes to the `WaterSampleSchema` class, then you'll need to re-generate the JSON schema. To re-generate the JSON schema:
```python
python3 -m nwss.dump_to_jsonschema
```

This will write the JSON schema to STDOUT. If you need to tweak or fix bugs in the JSON schema that is output by that script, then you'll need to make the changes within that code.

### Demo

Run a local server and auto-bundle your scripts:

```bash
npm run develop
```

Navigate to the app: http://localhost:8000/docs/
