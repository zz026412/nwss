import json
from marshmallow_jsonschema import JSONSchema
from marshmallow import fields
from nwss.schemas import WaterSampleSchema

schema = WaterSampleSchema(many=True)

class AllowManySchema(JSONSchema):
    type = fields.Constant('array')

json_schema = AllowManySchema()

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
    ],
    # 'oneOf': [
    #     {
    #         'properties': {
    #             'county_names': {
    #                 'title': 'county_names',
    #                 'type': ['string'],
    #                 'minLength': 1,
    #             }
    #         },
    #         'required': ['county_names'],
    #     },
    #     {
    #         'properties': {
    #             'other_jurisdiction': {
    #                 'title': 'other_jurisdiction',
    #                 'type': ['string'],
    #                 'minLength': 1,
    #             }
    #         },
    #         'required': ['other_jurisdiction'],
    #     },
    # ],
}

s['definitions']['WaterSampleSchema'].update(**custom_validators)

# get the properties so we can do two things:
# 1. nest it in the "items" key so that it's compatible with an array type
# 2. add "null" to fields with enums that allow_none
properties = s['definitions']['WaterSampleSchema']['properties']
del s['definitions']['WaterSampleSchema']['properties']

for key, property in properties.items():
    print('property')
    print(property)
    print()
    if 'null' in property['type'] and property.get('enum'):
        property['enum'].append(None)
        
# add back to the dict
# TODO: is there a way to do this so it's more immutable?
# mutating a dict like this makes my head hurt.
s['definitions']['WaterSampleSchema'].update({
    'items': {
        'properties': {**properties}
    }
})

# for property in s['definitions']['WaterSampleSchema']['properties']:
#     print('property')
#     print(property)
#     property_definition = s['definitions']['WaterSampleSchema']['properties'].get(property)
#     print(s['definitions']['WaterSampleSchema']['properties'].get(property))
#     if 'null' in property_definition['type'] and property_definition.get('enum'):
#         s['definitions']['WaterSampleSchema']['properties'][property]['enum'].append(None)  # json.dump should translate this to null in the output

with open('schema.json', 'w') as f:
    json.dump(s, f, indent=4)
