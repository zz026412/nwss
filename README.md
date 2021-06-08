# 💧 nwss-data-standard

A `marshmallow` schema for the [National Wastewater Surveillance System](https://www.cdc.gov/coronavirus/2019-ncov/cases-updates/wastewater-surveillance.html).

## Usage

### Installation

```bash
# Install from PyPI
pip install nwss

# Install local copy
git clone https://github.com/datamade/nwss-data-standard.git && cd nwss-data-standard
pip install .
```

See [Data dictionary version compatibility](#data-dictionary-version-compatibility)
for historical versions of the schema.

#### Data dictionary version compatibility

The CDC uses semantic versioning to track changes to [the expected format for
DCIPHER uploads](https://www.cdc.gov/coronavirus/2019-ncov/cases-updates/wastewater-surveillance/data-reporting-analytics.html#data-submission).
This table maps versions of the `nwss` Python package to versions of the data
dictionary.

| Package version | CDC version |
| - | - |
| 1.0.0 | 2.0.2 |

You can retrieve the CDC version from the `nwss` module for use in your scripts:

```python
>>> import nwss
>>> print(nwss.CDC_VERSION)
'2.0.2'
```

### Demo

#### On the web

Head to https://datamade.github.io/nwss-data-standard/ to validate a file
against the standard!

#### In Python

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
else:
    print('Data is valid!')
```

## Development

### Patches and pull requests

Your patches are welcome. Here's our suggested workflow:
 
* Fork the project.
* Create a new branch, then make your feature addition or bug fix.
* Send us a pull request with a description of your work.

### Python Schema

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

`nwss` comes with a Python implementation of the NWSS schema, as well as a
convenience script to translate it to a JSON schema:

```bash
python3 -m nwss.dump_to_jsonschema > schema.json
```

Much of the JSON schema is determined by the `marshmallow` schema, however
some conditional validation is written into the convenience script. You may
need to update the script to make your desired change.

### Demo

Run a local server and auto-bundle your scripts:

```bash
npm run develop
```

Navigate to the app: http://localhost:8000/docs/

## Errors and bugs

If something is not behaving intuitively, it is a bug and should be reported.
Report it here by creating an issue: https://github.com/datamade/nwss-data-standard/issues

Help us fix the problem as quickly as possible by following [Mozilla's guidelines for reporting bugs.](https://developer.mozilla.org/en-US/docs/Mozilla/QA/Bug_writing_guidelines#General_Outline_of_a_Bug_Report)

## Copyright and attribution

Copyright (c) 2021 DataMade. Released under the [MIT License](https://github.com/datamade/nwss-data-standard/blob/master/LICENSE).
