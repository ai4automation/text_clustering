from io import BytesIO
from flask import Flask
from utils.clustering import find_labels
from flask_restplus import Api, Resource
from flask_restplus import reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import InternalServerError, BadRequest


class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


# settings
settings = {
    'version': '2.0',
    'title': 'Semantic Clustering API',
    'description': 'Short text clustering API',
    'api_namespace': 'text_clustering',
    'api_description': 'short text clustering and labelling',
    'allowed_extensions': {'json'}
}

# flask definitions
app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

# flask-restplus definitions
api = Api(app, version=settings['version'], title=settings['title'], description=settings['description'])
ns = api.namespace(settings['api_namespace'], description=settings['api_description'])

# request parser
cluster_parser = reqparse.RequestParser()
cluster_parser.add_argument('file', location='files', type=FileStorage, required=True, help='JSON file to cluster')
cluster_parser.add_argument('n', required=True, help='Maximum word length for cluster labels', type=int)
cluster_parser.add_argument('coverage', default='false', choices=['true', 'false'], help='Maximum coverage')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in settings['allowed_extensions']


@ns.route('/')
class Cluster(Resource):
    @ns.response(200, 'Success')
    @ns.response(400, 'Validation Error')
    @ns.response(500, 'Internal Server Error')
    @ns.expect(cluster_parser, validate=False)
    @ns.doc('cluster')
    def post(self):
        args = cluster_parser.parse_args()

        if not allowed_file(args['file'].filename):
            error = BadRequest()
            error.data = ['This filetype is not allowed. Please contact admin.']
            raise error

        try:
            n = args['n']
            coverage = True if args['coverage'] is 'true' else False
            mem_file = BytesIO()
            args['file'].save(mem_file)

            clusters, coverage = find_labels(mem_file.getvalue().decode('UTF-8'), n, coverage)
            output = {'coverage': coverage, 'clusters': clusters}

        except:
            error = InternalServerError()
            error.data = ['Some error. Please contact admin.']
            raise error

        return output, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=3000)
