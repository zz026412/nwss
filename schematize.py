import json
from marshmallow_jsonschema import JSONSchema
from marshmallow import fields
from nwss.schemas import WaterSampleSchema

schema = WaterSampleSchema(many=True)

json_schema = JSONSchema()

s = json_schema.dump(schema)

custom_validators = {
    'dependencies': {
        'hum_frac_mic_conc': [
            'hum_frac_mic_unit',
            'hum_frac_target_mic',
            'hum_frac_target_mic_ref',
        ],
        'hum_frac_chem_conc': [
            'hum_frac_chem_unit',
            'hum_frac_target_chem',
            'hum_frac_target_chem_ref',
        ],
        'other_norm_conc': [
            'other_norm_name',
            'other_norm_unit',
            'other_norm_ref'
        ],
    },
    'allOf': [
        {
            'if': {
                'properties': {
                    'sample_location': {'enum': ['upstream']},
                },
                'required': ['sample_location'],
            },
            'then': {
                'properties': {
                    'sample_location_specify': {
                        'type': ['string'],
                        'minLength': 1
                    }
                },
                'required': ['sample_location_specify'],
            },
        },
        {
            'if': {
                'properties': {
                    'pretreatment': {'enum': ['yes']},
                },
                'required': ['pretreatment'],
            },
            'then': {
                'properties': {
                    'pretreatment_specify': {
                        'type': ['string'],
                        'minLength': 1
                    }
                },
                'required': ['pretreatment_specify'],
            },
        },
        {
            'if': {
                'properties': {
                    'sample_matrix': {
                        'enum': [
                            'raw wastewater',
                            'post grit removal',
                            'primary effluent',
                            'secondary effluent',
                        ]
                    },
                },
                'required': ['sample_matrix'],
            },
            'then': {
                'properties': {
                    'flow_rate': {'type': ['number']},
                },
                'required': ['flow_rate'],
            },
        },
        {
            'properties': {
                'county_names': {
                    'title': 'county_names',
                    'type': ['string'],
                    'minLength': 1,
                }
            },
            'required': ['county_names'],
        },
        {
            'properties': {
                'other_jurisdiction': {
                    'title': 'other_jurisdiction',
                    'type': ['string'],
                    'minLength': 1,
                }
            },
            'required': ['other_jurisdiction'],
        },
    ],
    'anyOf': [
        {
            'properties': {'inhibition_detect': {'enum': ['yes']}},
            'required': ['inhibition_adjust'],
        },
        {
            'if': {
                'properties': {'inhibition_detect': {'enum': ['not tested']}},
                'required': ['inhibition_detect'],
            },
            'then': {
                'properties': {'inhibition_method': {'enum': ['none']}},
                'required': ['inhibition_method'],
            },
        },
    ]
}

s['definitions']['WaterSampleSchema'].update(**custom_validators)

# Modify the schema so that it can validate many rows instead of one.
# This requires some changes to the schema.
s['definitions']['WaterSampleSchema'].update({'type': 'array'})

# To allow many rows, need to modify the schema so that 
# the "properties" are nested in the "items" key.
# So first, get properties so we can work with it and 
# ultimately add it back to the schema.
properties = s['definitions']['WaterSampleSchema']['properties']
del s['definitions']['WaterSampleSchema']['properties']

# Add None to fields with enums that allow_none, so None 
# converts to "null" in json and the enums accept null.
for key, property in properties.items():
    if 'null' in property['type'] and property.get('enum'):
        property['enum'].append(None)
 
# Add the mutated properties back to the dict
s['definitions']['WaterSampleSchema'].update({
    'items': {
        'properties': {**properties}
    }
})

with open('schema.json', 'w') as f:
    json.dump(s, f, indent=4)
