from marshmallow import Schema, fields, validate

from nwss import value_sets, fields as nwss_fields


class WaterSampleSchema(Schema):
    reporting_jurisdiction = fields.String(
        required=True,
        validate=validate.OneOf(value_sets.reporting_jurisdiction)
    )
    county_names = nwss_fields.ListString()
