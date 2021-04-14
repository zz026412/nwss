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

### Development

Install the app locally.

```python
git clone https://github.com/datamade/nwss-data-standard.git && cd nwss-data-standard
pip install -e .[dev]
```

Make your changes, then run the tests.

```python 
pytest
```
