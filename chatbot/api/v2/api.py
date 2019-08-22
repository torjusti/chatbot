import chatbot.api.v2.models as models

from flask_restplus import Namespace, Resource, fields, abort, reqparse

from chatbot.model.model_factory import ModelFactory
from chatbot.util.config_util import Config


api = Namespace('v2', description='Chatbot APIv2')


factory = ModelFactory.get_instance()
factory.set_db()

prod_col = Config.get_mongo_collection("prod")
manual_col = Config.get_mongo_collection("manual")
conflict_col = Config.get_mongo_collection("conflicts")
unknown_col = Config.get_mongo_collection("unknown")


direct_response_model = api.model('DirectResponse', {
    'user_input': fields.String(description='User chat input'),
    'response': fields.String(description='Bot chat response')
})

conflict_model = api.model('Conflict', {
    'conflict_id': fields.String(description='Document ID for conflict'),
    'title': fields.String(description='Title of conflict content')
})

delete_model = api.model('Delete', {
    'acknowledged': fields.Boolean(description='True if DB operation was ok'),
    'deleted_count': fields.Integer(description='How many docs were removed')
})

document_model = api.model('Document', {
    'id': fields.String(description='Content doc ID'),
    'title': fields.String(description='Content doc title')
})


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class Response(Resource):
    @api.marshal_with(direct_response_model)
    def get(self, query):
        return models.DirectResponse(user_input=query)


class FullResponse(Resource):
    def get(self):
        pass


class ConflictIDs(Resource):
    @api.marshal_with(conflict_model)
    def get(self):
        conflict_ids = factory.get_collection(conflict_col).find()
        return [models.Conflict(conflict['conflict_id'], conflict['title'])
                for conflict in conflict_ids]

    @api.marshal_with(delete_model)
    @api.response(200, 'Success', delete_model)
    @api.response(404, 'Conflict not found')
    def delete(self, conflict_id):
        result = factory.delete_document({"conflict_id": conflict_id},
                                         conflict_col)
        if result.deleted_count > 0:
            return result
        else:
            abort(404, 'Conflict not found')


url_parser = reqparse.RequestParser()
url_parser.add_argument('url', required=True)


class Documents(Resource):
    @api.marshal_with(document_model)
    @api.expect(url_parser)
    def get(self):
        url = url_parser.parse_args()['url']
        docs = factory.get_collection(prod_col).find({'url': url})

        return [models.Document(doc['id'], doc['content']['title'])
                for doc in docs]

    @api.marshal_with(delete_model)
    @api.response(200, 'Success', delete_model)
    @api.response(404, 'Document not found')
    def delete(self, document_id):
        query = {'id': document_id}
        result = factory.delete_document(query, manual_col)
        factory.update_document(query, {'manually_changed': False})

        if result.deleted_count > 0:
            return result
        else:
            abort(404, 'Document not found')


keyword_model = api.model('Keyword', {
                    'keyword': fields.String,
                    'confidence': fields.Float
})

content_model = api.model('Content', {
                    'title': fields.String,
                    'keywords': fields.List(fields.Nested(keyword_model)),
                    'texts': fields.List(fields.String)
})

content_collection_model = api.model('ContentCol', {
            'prod': fields.Nested(content_model),
            'manual': fields.Nested(content_model),
            'url': fields.String
})

content_data_model = api.model('ContentDataModel', {
            'data': fields.Nested(content_model)
})


class Content(Resource):
    @api.marshal_with(content_collection_model)
    @api.response(404, 'Content not found')
    def get(self, content_id):
        query = {'id': content_id}
        prod = next(factory.get_collection(prod_col).find(query), None)
        manual = next(factory.get_collection(manual_col).find(query), None)

        response = {}
        if prod:
            response['prod'] = prod['content']
        else:
            abort(404, 'Content not found')

        response['manual'] = manual['content'] if manual else None
        response['url'] = prod['url'] if prod else None

        return response

    # TODO: Write to use model factory function update_document
    @api.expect(content_data_model)
    @api.marshal_with(content_data_model)
    @api.response(400, 'Content IDs does not match!')
    @api.response(404, 'Content not found')
    def put(self, content_id):
        # Grab the data from request payload
        input_data = api.payload

        new_content = input_data['data']['content']
        input_content_id = input_data['data']['id']

        if not input_content_id == content_id:
            abort(400, 'Content IDs does not match!')

        query = {'id': content_id}
        # Check if the content that is requested changed actually exists
        old_content = factory.get_database() \
                             .get_collection(prod_col) \
                             .find(query)
        old_content = next(old_content, None)
        if not old_content:
            abort(404, 'Content not found')

        index = ({'id': content_id}, {'$set': {'content': new_content}})
        status = factory.get_database() \
                        .get_collection(manual_col)\
                        .update(*index)
        if status['updatedExisting'] is False:
            # If the document wasn't already in the manual collection, we need
            # to copy the automatic one first from prod
            old_content['content'] = new_content
            factory.get_database() \
                   .get_collection(manual_col) \
                   .insert_one(new_content)

        # set manually_changed to true
        index = ({'id': content_id}, {'$set': {'manually_changed': True}})
        factory.get_database().get_collection(prod_col).update(*index)

        # delete this document from the conflict collection
        query = {"conflict_id": content_id}
        factory.get_database().get_collection(conflict_col).delete_one(query)

        return new_content


api.add_resource(HelloWorld,
                 '/',
                 methods=['GET'])
api.add_resource(Response,
                 '/response/<string:query>/',
                 methods=['GET'])
api.add_resource(FullResponse,
                 '/response/',
                 methods=['GET'])
api.add_resource(ConflictIDs,
                 '/conflict_ids/',
                 methods=['GET'])
api.add_resource(ConflictIDs,
                 '/conflict_ids/<conflict_id>/',
                 methods=['DELETE'])
api.add_resource(Documents,
                 '/documents/',
                 methods=['GET'])
api.add_resource(Documents,
                 '/documents/<document_id>/',
                 methods=['DELETE'])
api.add_resource(Content,
                 '/content/<content_id>/',
                 methods=['GET', 'PUT'])
