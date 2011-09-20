from zope.component import getAdapter
from zope.schema.interfaces import ICollection, IObject
from beatbox.python_client import QueryRecord, QueryRecordSet
from collective.salesforce.content import logger
from collective.salesforce.content.interfaces import ISalesforceValueConverter

def prevent_dupe(l, value):
    if value not in l:
        l.append(value)

def queryFromSchema(schema, relationship_name=None, add_prefix=True, sf_object_id=None):
    """
    Given a schema tagged with Salesforce values, generate a query to return
    all the records for objects of that type.
    """
    
    sf_object = schema.queryTaggedValue('salesforce.object', None)
    sf_criteria = schema.queryTaggedValue('salesforce.criteria', None)
    sf_fields = schema.queryTaggedValue('salesforce.fields', {})
    sf_relationships = schema.queryTaggedValue('salesforce.relationships', {})
    sf_subqueries = schema.queryTaggedValue('salesforce.subqueries', {})
    
    if sf_object and (sf_fields or sf_relationships or sf_subqueries):
        if add_prefix:
            prefix = '%s.' % sf_object
        else:
            prefix = ''
        selects = ['%sId' % prefix]
        for schema_field_name in schema:
            if schema_field_name in sf_subqueries:
                # Has a custom subquery, which takes precedence
                prevent_dupe(selects, sf_subqueries[schema_field_name])
            elif schema_field_name in sf_fields.keys():
                # Has both sf:field and sf:relationship
                if schema_field_name in sf_relationships.keys():
                    prevent_dupe(selects, '(SELECT %s FROM %s%s)' % (
                        sf_fields[schema_field_name],
                        prefix,
                        sf_relationships[schema_field_name],
                    ))
                # Has sf:field but not sf:relationship
                else:
                    prevent_dupe(selects, '%s%s' % (
                        prefix,
                        sf_fields[schema_field_name],
                    ))
            # Has sf:relationship but not sf:field
            elif schema_field_name in sf_relationships.keys():
                field = schema[schema_field_name]
                # Zope field is an collection whose value_type is IObject:
                # build subquery based on the object schema
                if ICollection.providedBy(field) and IObject.providedBy(field.value_type):
                    subquery = queryFromSchema(
                        field.value_type.schema,
                        relationship_name = sf_relationships[schema_field_name],
                        add_prefix = False)
                    prevent_dupe(selects, '(%s)' % subquery)
                # Otherwise not supported
                else:
                    raise ValueError('sf:relationship may only be specified without '
                                     'sf:field if the field is a zope.schema.Object.')

        # Construct the main query.
        query = "SELECT %s FROM %s" % (
            ', '.join(selects),
            relationship_name or sf_object
        )
        if sf_criteria:
            query += " WHERE %s" % sf_criteria
            if sf_object_id is not None:
                query += " AND Id='%s'" % sf_object_id
        elif sf_object_id is not None:
            query += " WHERE Id='%s'" % sf_object_id

        logger.debug(query)
        return query
        
    return None


_marker = object()

def valueFromRecord(parent, path):
    """
    Given the parent record and a path (list of field names) to the value,
    extract the appropriate value. This may be a list if there is a
    parent-to-child relationship in the query.
    """
    
    if not path:
        raise ValueError, 'Missing path to value'
        
    value = parent.get(path[0], _marker)
    if value is _marker:
        raise KeyError, "'%s' not found in record '%s'" % (path[0], parent)
    
    next_path = path[1:]
    if next_path:
        if type(value) is QueryRecord:
            return valueFromRecord(value, next_path)
        if type(value) is QueryRecordSet:
            result = []
            for item in value:
                result.append(valueFromRecord(item, next_path))
            return result
    return value


def convertToSchemaValue(field, sf_value):
    """Converts a value from Salesforce into a value for Plone."""
    schema = field.interface
    sf_converters = schema.queryTaggedValue('salesforce.converters', {})
    converter_name = sf_converters.get(field.__name__, u'')
    converter = getAdapter(field, ISalesforceValueConverter, name=converter_name)
    return converter.toSchemaValue(sf_value)


def convertRecord(record, schema):
    """Converts the QueryRecords from a query result into a dict based on the schema.
    """
    sf_fields = schema.queryTaggedValue('salesforce.fields', {})
    sf_relationships = schema.queryTaggedValue('salesforce.relationships', {})
    sf_subqueries = schema.queryTaggedValue('salesforce.subqueries', {})
    
    d = {}
    for fname in schema:
        field = schema[fname]
        if fname in sf_fields:
            
            # Determine the 'path' to the field value.
            field_parts = sf_fields[fname].split('.')
            if fname in sf_relationships.keys():
                field_parts = sf_relationships[fname].split('.') + field_parts
            
            # Try to get a corresponding value from the record.
            try:
                value = valueFromRecord(record, field_parts)
            except KeyError:
                continue
            
            d[fname] = convertToSchemaValue(field, value)
        elif fname in sf_relationships:
            if ICollection.providedBy(field) and IObject.providedBy(field.value_type):
                subschema = field.value_type.schema
                subvalues = []
                for subrecord in valueFromRecord(record, sf_relationships[fname].split('.')):
                    subvalues.append(convertRecord(subrecord, subschema))
                d[fname] = subvalues
            else:
                pass
        elif fname in sf_subqueries:
            # custom query, we don't know how to find the relevant value on
            # the record so we just give the converter the whole record and
            # let it do its thing.
            # (Things will blow up if there isn't a custom converter!)
            d[fname] = convertToSchemaValue(field, record)
    return d
