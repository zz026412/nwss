from marshmallow import fields


class ListString(fields.String):
    '''
    Field that serializes comma-separated value to Python list and deserializes
    to a comma-separated value.
    '''

    def _serialize(self, value, attr, data, **kwargs):
        return ','.join(value)

    def _deserialize(self, value, attr, obj, **kwargs):
        if value:
            return value.split(',')
