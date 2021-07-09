from marshmallow import fields

from nwss import validators as nwss_validators


class CategoricalString(fields.String):

    def __init__(self, *args, **kwargs):
        try:
            allowed_values = kwargs.pop('allowed_values')
        except KeyError:
            raise TypeError("Missing required keyword argument 'allowed_values'")

        # Add allowed value validation
        kwargs['validate'] = nwss_validators.CaseInsensitiveOneOf(allowed_values)

        # Get error_messages, if provided, or create a fresh dict
        error_messages = kwargs.pop('error_messages', {})

        # Included allowed values if data missing
        error_messages['required'] = ('Missing data for required field. '
                                      f'Expected one of: {", ".join(allowed_values)}')
        kwargs['error_messages'] = error_messages

        # Initialize as normal
        super().__init__(*args, **kwargs)


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
