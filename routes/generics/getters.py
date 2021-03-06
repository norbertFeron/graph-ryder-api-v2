from neo4j.v1 import ResultError

from connector import neo4j
from flask_restful import Resource, reqparse
from routes.utils import makeResponse, addargs

import copy

parser = reqparse.RequestParser()
parser.add_argument('keys', action='append')
parser.add_argument('filters', action='append')
parser.add_argument('attrs', action='append')
parser.add_argument('hydrate')


class GetLabels(Resource):
    """
      @api {get} /getLabels/ Get all labels
      @apiName GetLabels
      @apiGroup Getters
      @apiDescription Return the list of possible labels.
      @apiParam {String} label Label
      @apiSuccess {Array} result Array of labels
   """
    def get(self):
        query = "MATCH (n) WITH n UNWIND labels(n) as l RETURN COLLECT(DISTINCT l) as labels"
        result = neo4j.query_neo4j(query)
        return makeResponse(result.single()['labels'], 200)


class GetLabelsHierarchy(Resource):
    """
      @api {get} /getLabelsHierarchy/ Get all labels
      @apiName GetLabels
      @apiGroup Getters
      @apiDescription Return the list of possible labels.
      @apiParam {String} label Label
      @apiSuccess {Array} result Array of labels
   """
    def get(self):
        struct = {}
        query = "MATCH (a) WITH DISTINCT LABELS(a) AS temp, COUNT(a) AS tempCnt UNWIND temp AS label " \
                "RETURN label, SUM(tempCnt) AS cnt"
        result = neo4j.query_neo4j(query)
        counts = {}
        for record in result:
            counts[record['label']] = record['cnt']
        query = "MATCH (n) RETURN DISTINCT labels(n) as labels"
        result = neo4j.query_neo4j(query)
        ungroupableId = 0
        for record in result:
            if all(counts[x] == counts[record['labels'][0]] for x in record['labels']): # todo also if 2 over 3 have the same count
                if len(record['labels']) == 1:
                    struct[record['labels'][0]] = {}
                if len(record['labels']) > 1:
                    struct['ungroupable' + str(ungroupableId)] = {}
                    for label in record['labels']:
                        struct['ungroupable' + str(ungroupableId)][label] = {}
                    ungroupableId += 1
            else:
                prev = {}
                for i, label in enumerate(sorted(record['labels'], key=lambda l: counts[l], reverse=True)):
                    if not i:
                        if label not in struct.keys():
                            struct[label] = {}
                        prev[i] = struct[label]
                    else:
                        if label not in prev[i-1]:
                            prev[i-1][label] = {}
                        prev[i] = prev[i-1][label]
        return makeResponse(struct, 200)


class GetLabelsByLabel(Resource):
    """
      @api {get} /getLabels/:label Get labels by label 
      @apiName GetLabelsByLabel
      @apiGroup Getters
      @apiDescription Return the list of possible labels for a generic one.
      @apiParam {String} label Label
      @apiSuccess {Array} result Array of labels
      @apiSuccessExample {json} Success-Response:
      http://api-url/getLabels/Link
      HTTP/1.1 200 OK
      ["Link", "Locate", "Acquaintance", "Financial", "Event", "Action", "Blood", "Sexual", "Support"]
   """
    def get(self, label):
        query = "MATCH (n:%s) WITH n UNWIND labels(n) as l RETURN COLLECT(DISTINCT l) as labels" % label
        result = neo4j.query_neo4j(query)
        return makeResponse(result.single()['labels'], 200)


class GetLabelsById(Resource):
    """
       @api {get} /getLabels/:id Get labels by id 
       @apiName GetLabels
       @apiGroup Getters
       @apiDescription Return the list of possible labels for a neo4j id.
       @apiParam {Integer} id Id
       @apiSuccess {Array} result Array of labels
       @apiSuccessExample {json} Success-Response:
       http://api-url/getLabels/123456
       HTTP/1.1 200 OK
       ["Link", "Locate"]
    """
    def get(self, id):
        query = "MATCH (n) WHERE ID(n) = %s WITH n UNWIND labels(n) as l RETURN COLLECT(DISTINCT l) as labels" % id
        result = neo4j.query_neo4j(query)
        return makeResponse(result.single()['labels'], 200)


class GetPropertiesByLabel(Resource):
    """
       @api {get} /getProperties Get properties by label
       @apiName GetPropertiesByLabel
       @apiGroup Getters
       @apiDescription Get possible property for a label  
       @apiParam {String} label Label
       @apiSuccess {Array} result Array of property.
    """
    def get(self, label):
        query = "MATCH (n:%s)-->(:Link:Prop)-->(p:Property) WITH p UNWIND labels(p) as k RETURN COLLECT(DISTINCT k) as keys" % label
        result = neo4j.query_neo4j(query)
        keys = result.single()['keys']
        if 'Property' in keys:
            keys.remove('Property')
        return makeResponse(keys, 200)


class GetAttributesByLabel(Resource):
    """
       @api {get} /getAttributes/:label Get attributes by label
       @apiName GetAttributesByLabel
       @apiGroup Getters
       @apiDescription Get possible attributes for a label  
       @apiParam {String} label Label
       @apiSuccess {Array} result Array of attributes.
    """
    def get(self, label):
        # query = "MATCH (n:%s)--(:Link:Attr)--(a:Attribute) WITH a UNWIND labels(a) as k RETURN COLLECT(DISTINCT k) as attr" % label # todo reset when Geo and Time is manage
        query = "MATCH (n:%s)--(:Link:Attr)--(a) WITH a UNWIND labels(a) as k RETURN COLLECT(DISTINCT k) as attr" % label
        result = neo4j.query_neo4j(query)
        attr = result.single()['attr']
        if 'Node' in attr:
            attr.remove('Node')
        if 'Attribute' in attr:
            attr.remove('Attribute')
        return makeResponse(attr, 200)


class GetAttributesTypes(Resource):
    """
       @api {get} /getAttributesTypes/ Get all possible type of attr
       @apiName GetAttributesTypes
       @apiGroup Getters
       @apiDescription Get possible types for all attributes
       @apiParam {String} label Label
       @apiSuccess {Array} result Array of types.
    """

    def get(self):
        query = "MATCH (la:Link:Attr) RETURN COLLECT(DISTINCT la.type) as types"
        result = neo4j.query_neo4j(query)
        return makeResponse(result.single()['types'], 200)


class GetPropertyValue(Resource):
    """
       @api {get} /getPropertyValue/:property Get value by property
       @apiName GetPropertyValueByLabel
       @apiGroup Getters
       @apiDescription Get possible property value for a label  
       @apiParam {String} label Label
       @apiParam {String} property Property
       @apiSuccess {Array} result Array of value.
    """
    def get(self, key):
        query = "MATCH (n)--(:Link:Prop)--(p:Property:%s) WITH p UNWIND p.value as v RETURN COLLECT(DISTINCT v) as values" % key
        result = neo4j.query_neo4j(query)
        return makeResponse(result.single()['values'], 200)


class GetPropertyValueByLabel(Resource):
    """
       @api {get} /getPropertyValue/:label/:property Get value by property/label
       @apiName GetPropertyValueByLabel
       @apiGroup Getters
       @apiDescription Get possible property value for a label  
       @apiParam {String} label Label
       @apiParam {String} property Property.
       @apiSuccess {Array} result Array of value.
    """
    def get(self, label, key):
        query = "MATCH (n:%s)--(:Link:Prop)--(p:Property:%s) WITH p UNWIND p.value as v RETURN COLLECT(DISTINCT v) as values" % (label, key)
        result = neo4j.query_neo4j(query)
        return makeResponse(result.single()['values'], 200)


class GetPropertyValueAndIdByLabel(Resource):
    """
       @api {get} /getPropertyValueAndId/:label/:property Get value and id by property/label
       @apiName GetPropertyValueByLabel
       @apiGroup Getters
       @apiDescription Get possible property value for a label
       @apiParam {String} label Label
       @apiParam {String} property Property.
       @apiSuccess {Array} result Array of value.
    """
    def get(self, label, key):
        query = "MATCH (n:%s)--(:Link:Prop)--(p:Property:%s) RETURN p.value as value, id(n) as id" % (label, key)
        result = neo4j.query_neo4j(query)
        response = []
        for record in result:
            response.append({'value': record['value'], 'id': record['id']})
        return makeResponse(response, 200)


class GetByLabel(Resource):  # todo convert date node to readable date when hydrate
    """
       @api {get} /get/:label Get elements by label 
       @apiName GetByLabel
       @apiGroup Getters
       @apiDescription Get elements for a label 
       @apiParam {String} label Label
       @apiParam {keys} keys Keys wanted for each property of the element (* for all)
       @apiParam {attrs} attr attributes wanted for each element (* for all)
       @apiParam {hydrate} hydrate != 0 to hydrate attrs with info
       @apiParam {Filters} filter Filters on property
       @apiSuccess {Array} result Array of element.
    """
    def get(self, label): # todo redo for float version
        args = parser.parse_args()
        keys = args['keys']
        filters = args['filters']
        query = "MATCH (n:%s)" % label
        if filters:
            query += "WHERE"
            for filter in filters:
                query += " n.%s = '%s' AND" % (filter.split(':')[0], filter.split(':')[1])
            query = query[:-4]
        query += " RETURN ID(n) as id"
        if keys:
            if '*' in keys:
                q = "MATCH (n:%s) WITH n UNWIND keys(n) as k RETURN COLLECT(DISTINCT k) as keys" % label
                result = neo4j.query_neo4j(q)
                keys = result.single()['keys']
            for key in keys:
                query += ", n.%s as %s" % (key, key)
        query += addargs()
        result = neo4j.query_neo4j(query)
        response = {}
        for record in result:
            if not record['id'] in response.keys():
                response[record['id']] = {}
            if keys:
                for key in keys:
                    response[record['id']][key] = record[key]
        attrs = args['attrs']
        if attrs and '*' in attrs:
            attrs = []
            q = "MATCH (n:%s)-[:HAS]->(:Property)-[:IS]->(k)" % label
            q += " RETURN COLLECT(DISTINCT labels(k)) as attr"
            result = neo4j.query_neo4j(q)
            attributes = result.single()['attr']
            for a in attributes:
                if 'Attribute' in a:
                    a.remove('Attribute')
                attrs.append(a[0])  # Unpack
        if attrs:
            for attribute in attrs:
                query = "MATCH (n:%s)" % label
                query += " WITH n"
                query += " MATCH (n)-[:HAS]->(:Property)-[:IS]->(%s:%s)" % (attribute, attribute)
                query += " RETURN ID(n) as id, collect(DISTINCT ID(%s)) as %s " % (attribute, attribute)
                result = neo4j.query_neo4j(query)
                for record in result:
                    if not record['id'] in response.keys():
                        response[record['id']] = {}
                    if not args['hydrate'] or args['hydrate'] == str(0):
                        response[record['id']][attribute] = record[attribute]
                    else:
                        response[record['id']][attribute] = []
                        for a in record[attribute]:
                            q = "MATCH (n) WHERE ID(n) = %s WITH n UNWIND keys(n) as k" % a
                            q += " RETURN COLLECT(DISTINCT k) as keys"
                            result = neo4j.query_neo4j(q)
                            keys = result.single()['keys']
                            query = "MATCH (n) WHERE ID(n) = %s RETURN ID(n) as id" % a
                            for key in keys:
                                query += ", n.%s as %s" % (key, key)
                            result = neo4j.query_neo4j(query)
                            try:
                                res = result.single()
                            except ResultError:
                                return makeResponse("Impossible to find this id", 400)
                            attr = {'id': res['id']}
                            if keys:
                                for key in keys:
                                    attr[key] = res[key]
                            response[record['id']][attribute].append(attr)
        return makeResponse(response, 200)


class GetById(Resource):
    """
       @api {get} /get/:id Get an element by id 
       @apiName GetById
       @apiGroup Getters
       @apiDescription Get element by neo4j id
       @apiParam {Integer} id id
       @apiParam {keys} keys Keys wanted for each property of the element (* for all)
       @apiParam {attrs} attr attributes wanted for each element (* for all)
       @apiParam {hydrate} hydrate != 0 to hydrate attrs with info
       @apiSuccess {Element} the element
    """
    def get(self, id):  # Multiple request
        args = parser.parse_args()
        ####### Properties #######
        keys = args['keys']
        result = []
        query = "MATCH (n) WHERE ID(n) = %s RETURN labels(n) as labels" % id
        labels = neo4j.query_neo4j(query).single()['labels']
        element = {'id': id}
        # ### Time ###
        # if 'Time' in labels and keys:
        #     query = "MATCH (t:Time)<-[:CHILD]-(p1) WHERE ID(t) = %s OPTIONAL MATCH (p1)<-[:CHILD]-(p2:Time) " % id
        #     query += " RETURN t.value as t, ID(t) as tid, labels(t) as labels_t, p1.value as p1, ID(p1) as p1id, labels(p1) as labels_p1, p2.value as p2, ID(p2) as p2id, labels(p2) as labels_p2"
        #     result = neo4j.query_neo4j(query).single()
        #     result['labels_t'].remove('Time')
        #     result['labels_t'].remove('Node')
        #     element[result['labels_t'][0]] = [{'pid': result['tid'], 'value': result['t']}]
        #     if result['p1']:
        #         result['labels_p1'].remove('Time')
        #         result['labels_p1'].remove('Node')
        #         element[result['labels_p1'][0]] = [{'pid': result['p1id'], 'value': result['p1']}]
        #         if result['p2']:
        #             result['labels_p2'].remove('Time')
        #             result['labels_p2'].remove('Node')
        #             element[result['labels_p2'][0]] = [{'pid': result['p2id'], 'value': result['p2']}]
        #
        # ### Geo ###
        # elif 'Geo' in labels and keys:
        #     print(labels)
        # else:
        if keys:
            query = "MATCH (n)--(l:Link:Prop)--(p:Property) WHERE ID(n) = %s" % id
            if '*' not in keys:
                query += " AND ('%s' IN labels(p)" % keys.pop(0)
                for key in keys:
                    query += " OR '%s' IN labels(p)" % key
                query += ')'
            query += " OPTIONAL MATCH (l)-->(la:Link:Attr)-->(a:Node)"
            query += " RETURN labels(p) as labels, p.value as value, ID(p) as pid, collect(id(la)) as laid"
            result = neo4j.query_neo4j(query)
            if not result:
                return makeResponse("Impossible to find this id", 400)
        for record in result:
            label = record['labels']
            label.remove('Property')
            if not label[0] in element.keys():
                element[label[0]] = []
            prop = {"pid": record['pid'], "value": record['value']}
            if record['laid']:
                prop['attrs'] = []
                for r in record['laid']:
                    q = "MATCH (la:Link:Attr)-->(a:Node) WHERE ID(la) = %s RETURN la.type as type, ID(a) as aid" % r
                    result = neo4j.query_neo4j(q)
                    for rec in result:
                        prop['attrs'].append({'type': rec['type'], 'aid': rec['aid']})
            element[label[0]].append(prop)
        args = parser.parse_args()

        ####### Attributes #######
        attrs = args['attrs']
        if attrs and '*' in attrs:
            attrs = []
            q = "MATCH (n)-[:HAS]->(:Link:Attr)-[:IS]->(k)"
            q += " WHERE ID(n) = %s RETURN COLLECT(DISTINCT labels(k)) as attr" % id
            result = neo4j.query_neo4j(q)
            attributes = result.single()['attr']
            for a in attributes:
                if 'Attribute' in a:
                    a.remove('Attribute')
                if 'Node' in a:
                    a.remove('Node')
                if 'Geo' in a:
                    a.remove('Geo')
                if 'Time' in a:
                    a.remove('Time')
                if 'SubGraph' in a:
                    a.remove('SubGraph')
                attrs.append(a[0])  # Unpack
        if attrs:
            for attribute in attrs:
                query = "MATCH (n) WHERE ID(n) = %s" % id
                query += " WITH n"
                query += " MATCH (n)-[:HAS]->(l:Link:Attr)-[:IS]->(%s:%s)" % (attribute.replace(':', ''), attribute)
                # if attribute.split(':')[0] == 'Geo' or attribute.split(':')[0] == 'Time':
                query += " RETURN l.type as type, collect(DISTINCT ID(l)) as aid%s, collect(DISTINCT ID(%s)) as %s " % (attribute.replace(':', ''), attribute.replace(':', ''), attribute.replace(':', ''))
                result = neo4j.query_neo4j(query)
                for record in result:
                    elements = []
                    i = 0
                    for e in record[attribute.replace(':', '')]:
                        elements.append({'id': e, 'laid': record['aid' + attribute.replace(':', '')][i]})
                        i += 1
                    element[attribute + ':' + record['type']] = elements
                # else:
                #     query += " RETURN collect(DISTINCT ID(%s)) as %s " % (attribute.replace(':', ''), attribute.replace(':', ''))
                #     result = neo4j.query_neo4j(query)
                #     try:
                #         res = result.single()
                #     except ResultError:
                #         return makeResponse("Impossible to find this id", 400)
                #     # if not args['hydrate'] or args['hydrate'] == 0:
                #     element[attribute] = res[attribute]
                    # else:
                    #     element[attribute] = []
                    #     for a in res[attribute]:
                    #         q = "MATCH (n)--(l:Link:Prop)--(p:Property) WHERE ID(n) = %s RETURN labels(p) as labels, p.value as value, ID(p) as pid" % a
                    #         result = neo4j.query_neo4j(q)
                    #         attr = {}
                    #         for record in result:
                    #             label = record['labels']
                    #             label.remove('Property')
                    #             if label[0] not in attr.keys():
                    #                 attr[label[0]] = []
                    #             attr[label[0]].append({'value': record['value'], 'pid': record['pid']})
                    #         element[attribute].append({a: attr})
        return makeResponse(element, 200)
