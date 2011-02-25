from collective.salesforce.behavior import logger
    
def queryFromSchema(schema):
    """
    Given a schema tagged with Salesforce values, generate a query to return
    all the records for objects of that type.
    """
    
    sf_object = schema.queryTaggedValue('salesforce.object', None)
    sf_criteria = schema.queryTaggedValue('salesforce.criteria', None)
    sf_fields = schema.queryTaggedValue('salesforce.fields', {})
    
    if sf_object and sf_fields:
        # Get a list of fields for the query.
        fields = ['%s.%s' % (sf_object, field) for field \
            in ['Id'] + sf_fields.values()]
    
        # Construct the main query.
        query = "SELECT %s FROM %s" % (
            ', '.join(fields),
            sf_object
        )
        if sf_criteria:
            query += " WHERE %s" % sf_criteria
            
        logger.debug(query)
        return query
        
    return None
