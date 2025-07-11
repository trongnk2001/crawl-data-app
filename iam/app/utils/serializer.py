from datetime import datetime


def serialize(model_instance, exclude_fields=None, include_relationships=False):
    from datetime import datetime

    if exclude_fields is None:
        exclude_fields = []

    result = {}
    for column in model_instance.__table__.columns:
        if column.name in exclude_fields:
            continue

        value = getattr(model_instance, column.name)
        result[column.name] = value.isoformat() if isinstance(value,
                                                              datetime) else value

    if include_relationships:
        for relation in model_instance.__mapper__.relationships:
            related = getattr(model_instance, relation.key)
            if related is None:
                result[relation.key] = None
            elif isinstance(related, list):
                result[relation.key] = [serialize(item) for item in related]
            else:
                result[relation.key] = serialize(related)

    return result
