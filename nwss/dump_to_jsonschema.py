import json
import sys
from marshmallow_jsonschema import JSONSchema
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
                'items': {
                    'properties': {
                        'sample_location': {'enum': ['upstream']},
                    },
                    'required': ['sample_location'],
                }
            },
            'then': {
                'items': {
                    'properties': {
                        'sample_location_specify': {
                            'type': ['string'],
                            'minLength': 1
                        }
                    },
                    'required': ['sample_location_specify'],
                }
            },
        },
        {
            'if': {
                'items': {
                    'properties': {
                        'pretreatment': {'enum': ['yes']},
                    },
                    'required': ['pretreatment'],
                }
            },
            'then': {
                'items': {
                    'properties': {
                        'pretreatment_specify': {
                            'type': ['string'],
                            'minLength': 1
                        }
                    },
                    'required': ['pretreatment_specify'],
                }
            },
        },
        {
            'if': {
                'items': {
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
                }
            },
            'then': {
                'items': {
                    'properties': {
                        'flow_rate': {'type': ['number']},
                    },
                    'required': ['flow_rate'],
                }
            },
        },
        {
            'if': {
                'items': {
                    'properties': {'inhibition_detect': {'enum': ['yes']}},
                    'required': ['inhibition_detect'],
                }
            },
            'then': {
                'items': {
                    'properties': {
                        'inhibition_adjust': {
                            'type': ['string'],
                            'minLength': 1
                        },
                        'inhibition_method': {
                            'type': ['string'],
                            'minLength': 1
                        }
                    },
                    'required': ['inhibition_adjust'],
                }
            }
        },
        {
            'if': {
                'items': {
                    'properties': {'inhibition_detect': {'enum': ['not tested']}}
                }
            },
            'then': {
                'items': {
                    'properties': {'inhibition_method': {'enum': ['none']}}
                }
            }
        }
    ]
}

# Get properties so we can mutate it and 
# ultimately add it back to the schema.
properties = s['definitions']['WaterSampleSchema'].pop('properties')

# Add None to fields that can be empty. These fields 
# must have null as an enum in the JSON schema.
for key, property in properties.items():
    if 'null' in property['type'] and property.get('enum'):
        property['enum'].append(None)
 
# Reshape the schema so it accepts an array, 
# and add the custom_validators.
s['definitions']['WaterSampleSchema'].update({
    'type': 'array',
    'items': {
        'properties': {**properties},
    },
    **custom_validators
})

def dump_schema():
    json.dump(s, sys.stdout)

if __name__ == "__main__":
    dump_schema()
