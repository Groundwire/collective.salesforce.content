from zope.schema.interfaces import ICollection, IObject
from beatbox.python_client import QueryRecord, QueryRecordSet
from collective.salesforce.behavior import logger
    
def queryFromSchema(schema, relationship_name=None, add_prefix=True):
    """
    Given a schema tagged with Salesforce values, generate a query to return
    all the records for objects of that type.
    """
    
    sf_object = schema.queryTaggedValue('salesforce.object', None)
    sf_criteria = schema.queryTaggedValue('salesforce.criteria', None)
    sf_fields = schema.queryTaggedValue('salesforce.fields', {})
    sf_relationships = schema.queryTaggedValue('salesforce.relationships', {})
    
    if sf_object and (sf_fields or sf_relationships):
        if add_prefix:
            prefix = '%s.' % sf_object
        else:
            prefix = ''
        selects = ['%sId' % prefix]
        for schema_field_name in schema:
            if schema_field_name in sf_fields.keys():
                # Has both sf:field and sf:relationship
                if schema_field_name in sf_relationships.keys():
                    selects.append('(SELECT Id, %s FROM %s%s)' % (
                        sf_fields[schema_field_name],
                        prefix,
                        sf_relationships[schema_field_name],
                    ))
                # Has sf:field but not sf:relationship
                else:
                    selects.append('%s%s' % (
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
                    selects.append('(%s)' % subquery)
                # Otherwise just get the Ids
                else:
                    selects.append('(SELECT Id FROM %s%s)' % (
                        prefix,
                        sf_relationships[schema_field_name],
                    ))

        # Construct the main query.
        query = "SELECT %s FROM %s" % (
            ', '.join(selects),
            relationship_name or sf_object
        )
        if sf_criteria:
            query += " WHERE %s" % sf_criteria
            
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
