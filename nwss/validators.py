from marshmallow import validate, ValidationError


class CaseInsensitiveOneOf(validate.OneOf):
    _jsonschema_base_validator_class = validate.OneOf

    def __call__(self, value) -> str:
        try:
            if not any(value.casefold() == v.casefold() for v in self.choices):
                raise ValidationError(self._format_error(value))
        except TypeError as error:
            raise ValidationError(self._format_error(value)) from error

        return value
