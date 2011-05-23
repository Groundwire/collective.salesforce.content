from beatbox.python_client import QueryRecord, QueryRecordSet
from collective.salesforce.behavior import logger
    
def queryFromSchema(schema):
    """
    Given a schema tagged with Salesforce values, generate a query to return
    all the records for objects of that type.
    """
    
    sf_object = schema.queryTaggedValue('salesforce.object', None)
    sf_criteria = schema.queryTaggedValue('salesforce.criteria', None)
    sf_fields = schema.queryTaggedValue('salesforce.fields', {})
    sf_relationships = schema.queryTaggedValue('salesforce.relationships', {})
    
    if sf_object and (sf_fields or sf_relationships):
        selects = ['%s.Id' % (sf_object)]
        for schema_field in schema:
            if schema_field in sf_fields.keys():
                # Has both sf:field and sf:relationship
                if schema_field in sf_relationships.keys():
                    selects.append('(SELECT %s FROM %s.%s)' % (
                        sf_fields[schema_field],
                        sf_object,
                        sf_relationships[schema_field],
                    ))
                # Has sf:field but not sf:relationship
                else:
                    selects.append('%s.%s' % (
                        sf_object,
                        sf_fields[schema_field],
                    ))
            # Has sf:relationship but not sf:field
            elif schema_field in sf_relationships.keys():
                raise ValueError, 'You cannot define sf:relationship ' \
                    'without defining sf:field.'

        # Construct the main query.
        query = "SELECT %s FROM %s" % (
            ', '.join(selects),
            sf_object
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
