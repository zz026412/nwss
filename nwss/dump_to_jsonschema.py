import json
import sys
from marshmallow_jsonschema import JSONSchema
from nwss.schemas import WaterSampleSchema

schema = WaterSampleSchema(many=True)

json_schema = JSONSchema()

s = json_schema.dump(schema)

custom_validators = {
    'allOf': [
        {
            'if': {
                'properties': {
                    'hum_frac_mic_conc': {
                        'type': ['string'],
                        'minLength': 1
                    },
                },
                'required': ['hum_frac_mic_conc']
            },
            'then': {
                'properties': {
                    'hum_frac_mic_unit': {
                        'type': ['string'],
                        'minLength': 1
                    },
                    'hum_frac_target_mic': {
                        'type': ['string'],
                        'minLength': 1
                    },
                    'hum_frac_target_mic_ref': {
                        'type': ['string'],
                        'minLength': 1
                    },
                },
                'required': [
                    'hum_frac_mic_unit',
                    'hum_frac_target_mic',
                    'hum_frac_target_mic_ref'
                ]
            }
        },
        {
            'if': {
                'properties': {
                    'hum_frac_chem_conc': {
                        'type': ['string'],
                        'minLength': 1
                    }
                },
                'required': ['hum_frac_chem_conc']
            },
            'then': {
                'properties': {
                    'hum_frac_chem_unit': {
                        'type': ['string'],
                        'minLength': 1
                    },
                    'hum_frac_target_chem': {
                        'type': ['string'],
                        'minLength': 1
                    },
                    'hum_frac_target_chem_ref': {
                        'type': ['string'],
                        'minLength': 1
                    },
                },
                'required': [
                    'hum_frac_chem_unit',
                    'hum_frac_target_chem',
                    'hum_frac_target_chem_ref'
                ]
            }
        },
        {
            'if': {
                'properties': {
                    'other_norm_conc': {
                        'type': ['string'],
                        'minLength': 1
                    }
                },
                'required': ['other_norm_conc']
            },
            'then': {
                'properties': {
                    'other_norm_name': {
                        'type': ['string'],
                        'minLength': 1
                    },
                    'other_norm_unit': {
                        'type': ['string'],
                        'minLength': 1
                    },
                    'other_norm_ref': {
                        'type': ['string'],
                        'minLength': 1
                    },
                },
                'required': [
                        'other_norm_name',
                        'other_norm_unit',
                        'other_norm_ref'
                    ]
            }
        },
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
            'if': {
                'properties': {'inhibition_detect': {'enum': ['yes']}},
                'required': ['inhibition_detect'],
            },
            'then': {
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
                'required': [
                    'inhibition_adjust',
                    'inhibition_method'
                ],
            }
        },
        {
            'if': {
                'properties': {
                    'inhibition_detect': {'enum': ['not tested']}
                }
            },
            'then': {
                'properties': {'inhibition_method': {'enum': ['none']}}
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
    if property.get('enum'):
        property.update({
            'case_insensitive_enums': True
        })

        if 'null' in property['type']:
            property['enum'].append(None)

    if property.get('format') == 'time':
        # Add a regex to validate the time string based on the pattern.
        hh_mm_ss_regex = '^([0-1]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$'
        property['pattern'] = hh_mm_ss_regex
        # Remove the format key so the regex validates instead.
        property.pop('format')

s['definitions']['WaterSampleSchema'].update({
    'properties': {**properties},
    **custom_validators
})

# Reshape the schema so it accepts an array
# of the WaterSampleSchema objects.
s['definitions'].update({
    'schema': {
        'type': 'array',
        'items': {
          '$ref': '#/definitions/WaterSampleSchema'
        }
    }
})

# Change the top-level ref to use 'schema',
# instead of '#/definitions/WaterSampleSchema'.
s.update({
    '$ref': '#/definitions/schema',
})


def dump_schema():
    json.dump(s, sys.stdout, indent=4)


if __name__ == "__main__":
    dump_schema()
