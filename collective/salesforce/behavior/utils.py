from collective.salesforce.behavior import logger
    
def queryFromSchema(schema, sf_ids=[]):
    """
    Given a schema tagged with Salesforce values, generate a query to return
    all the records for objects of that type. If Salesforce IDs is specified,
    we only query for records with those IDs.
    """
    
    sf_object = schema.queryTaggedValue('salesforce.object', None)
    sf_criteria = schema.queryTaggedValue('salesforce.criteria', None)
    sf_fields = schema.queryTaggedValue('salesforce.fields', {})
    
    if sf_object and sf_fields:
        # Get a list of fields for the query.
        raw_fields = ['Id'] + sf_fields.values()
        fields = ['%s.%s' % (sf_object, field) for field \
            in raw_fields if not field.startswith('(')]
        # Fields will start with '(' if they are outer joins. Let's not
        # prefix them with the object name.
        fields += [field for field  in raw_fields if field.startswith('(')]

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

def parseSFFieldNames(field_map):
    """
    If SF "field names" coming from XML schema really contain outer joins,
    translate them to the name used in the SF result set.
    
    We're assuming that outer joins look something like:
    "(SELECT foo from sf_object.field_name)"
    
    in which case we'll translate it to "field_name"
    """
    for f,v in field_map.items():
        if v.startswith('('):
            new_val = v[v.rfind(' '):v.rfind(')')].strip()
            # strip prefix
            new_val = new_val.split('.')[-1]
            field_map[f] = new_val
    return field_map