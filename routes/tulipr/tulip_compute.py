import uuid
from flask_restful import Resource
from routes.utils import makeResponse
from graphtulip.degreeOfInterest import create


class ComputeDOI(Resource):
    def get(self, type, id):
        graph_id = uuid.uuid4()
        create("complete", graph_id, type, id)
        return makeResponse([graph_id.urn[9:]])


class ComputeUserDOI(Resource):
    def get(self, type, id):
        graph_id = uuid.uuid4()
        create("usersToUsers", graph_id, type, id)
        return makeResponse([graph_id.urn[9:]])