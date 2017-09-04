import datetime
import decimal
from peewee import Field, Node, ForeignKeyField
from playhouse.shortcuts import _clone_set


def get_fields_instances(model_class, fields):
    only = set()
    for field in fields:
        if isinstance(field, (str, unicode)):
            field_instance = getattr(model_class, field, None)
            if field_instance:
                only.add(field_instance)
        elif isinstance(field, Field):
            only.add(field)
        else:
            continue
    return only


def model_to_dict(model, recurse=True, backrefs=False, only=None,
                  exclude=None, seen=None, extra_attrs=None,
                  fields_from_query=None, max_depth=None,
                  append_attrs=None):
    max_depth = -1 if max_depth is None else max_depth
    if max_depth == 0:
        recurse = False

    model_class = type(model)

    only = get_fields_instances(model_class, _clone_set(only))

    extra_attrs = _clone_set(extra_attrs)
    data = {}
    exclude = _clone_set(exclude)
    seen = _clone_set(seen)
    exclude |= seen

    if fields_from_query is not None:
        for item in fields_from_query._select:
            if isinstance(item, Field):
                only.add(item)
            elif isinstance(item, Node) and item._alias:
                extra_attrs.add(item._alias)

    for field in model._meta.declared_fields:
        if field in exclude or (only and (field not in only)):
            continue

        field_data = model._data.get(field.name)
        if isinstance(field, ForeignKeyField) and recurse:
            if field_data:
                seen.add(field)
                rel_obj = getattr(model, field.name)
                field_data = model_to_dict(
                    rel_obj,
                    recurse=recurse,
                    backrefs=backrefs,
                    exclude=exclude,
                    seen=seen,
                    max_depth=max_depth - 1)
            else:
                field_data = None
        if isinstance(field_data, (datetime.date, datetime.datetime)):
            field_data = field_data.isoformat()
        if isinstance(field_data, decimal.Decimal):
            field_data = '{0:.2f}'.format(field_data)
        data[field.name] = field_data

    if extra_attrs:
        for attr_name in extra_attrs:
            attr = getattr(model, attr_name)
            if callable(attr):
                data[attr_name] = attr()
            else:
                data[attr_name] = attr

    if backrefs and recurse:
        for related_name, foreign_key in model._meta.reverse_rel.items():
            descriptor = getattr(model_class, related_name)
            if descriptor in exclude or foreign_key in exclude:
                continue
            if only and (descriptor not in only) and (foreign_key not in only):
                continue

            accum = []
            exclude.add(foreign_key)
            related_query = getattr(
                model,
                related_name + '_prefetch',
                getattr(model, related_name))

            for rel_obj in related_query:
                accum.append(model_to_dict(
                    rel_obj,
                    recurse=recurse,
                    backrefs=backrefs,
                    exclude=exclude,
                    max_depth=max_depth - 1))

            data[related_name] = accum
    if append_attrs:
        data.update(append_attrs)
    return data


def parse_date(date_text):
    try:
        return datetime.datetime.strptime(date_text, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD, got {}".format(date_text))
