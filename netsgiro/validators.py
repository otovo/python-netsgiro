from attr.validators import instance_of


def str_of_length(length):
    def validator(instance, attribute, value):
        instance_of(str)(instance, attribute, value)
        if len(value) != length:
            raise ValueError(
                '{0.name} must be exactly {1} chars, got {2!r}'
                .format(attribute, length, value))
    return validator
