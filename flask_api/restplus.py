from io import BytesIO
import os

from flask import Flask, url_for, send_from_directory
from flask_restplus import Api, Resource
from werkzeug.exceptions import InternalServerError, BadRequest
from werkzeug.utils import secure_filename

import flask_api.parsers as parsers
import flask_api.settings as settings
from flask_api.api_utils import ReverseProxied, allowed_file, get_uuid_filename

from utils.clustering import find_labels
import utils.event_cluster


# flask definitions
app = Flask(__name__, static_url_path='')
# app.wsgi_app = ReverseProxied(app.wsgi_app)
app.config['SERVER_NAME'] = settings.SERVER_NAME

# flask-restplus definitions
api = Api(app, version=settings.VERSION, title=settings.TITLE, description=settings.DESCRIPTION)
text_cluster_ns = api.namespace(settings.TEXT_API_NAMESPACE, description=settings.TEXT_API_DESCRIPTION)
event_cluster_ns = api.namespace(settings.EVENT_API_NAMESPACE, description=settings.EVENT_API_DESCRIPTION)
download_ns = api.namespace(settings.DOWNLOAD_API_NAMESPACE, description=settings.DOWNLOAD_API_DESCRIPTION)


@text_cluster_ns.route('/cluster')
class ClusterText(Resource):
    @text_cluster_ns.response(200, 'Success')
    @text_cluster_ns.response(400, 'Validation Error')
    @text_cluster_ns.response(500, 'Internal Server Error')
    @text_cluster_ns.expect(parsers.cluster_parser, validate=False)
    def post(self):
        args = parsers.cluster_parser.parse_args()

        if not allowed_file(args['file'].filename, settings.TEXT_ALLOWED_EXTENSIONS):
            error = BadRequest()
            error.data = ['This filetype is not allowed. Please contact admin.']
            raise error

        n = args['n']
        if n < 2 or n > 6:
            error = BadRequest()
            error.data = ['n value must be between 2 and 6. Please try again.']
            raise error

        try:
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


@event_cluster_ns.route('/cluster')
class ClusterEvent(Resource):
    @event_cluster_ns.response(200, 'Success')
    @event_cluster_ns.response(400, 'Validation Error')
    @event_cluster_ns.response(500, 'Internal Server Error')
    @event_cluster_ns.expect(parsers.event_parser, validate=False)
    def post(self):
        args = parsers.event_parser.parse_args()

        if not allowed_file(args['file'].filename, settings.EVENT_ALLOWED_EXTENSIONS):
            error = BadRequest()
            error.data = ['This file type is not allowed. Please contact admin.']
            raise error

        try:
            comments_field = args['comments']
            action_field = args['action']
            filename = secure_filename(args['file'].filename)
            filename = get_uuid_filename(filename)
            file_path = os.path.join(settings.UPLOAD_FOLDER, filename)
            if not os.path.exists(settings.UPLOAD_FOLDER):
                os.makedirs(settings.UPLOAD_FOLDER)
            args['file'].save(file_path)

            derived_filename = utils.event_cluster.run_e2e(file_path, comments_field, action_field)
            output = {'download_url': url_for('download_file', filename=os.path.basename(derived_filename))}

        except:
            error = InternalServerError()
            error.data = ['Some error. Please contact admin.']
            raise error

        return output, 200


@download_ns.route('/<filename>')
@download_ns.doc(params={'filename': 'CSV file to download'})
class DownloadFile(Resource):
    @download_ns.response(200, 'Success')
    @download_ns.response(400, 'Validation Error')
    @download_ns.response(500, 'Internal Server Error')
    def get(self, filename):
        if not allowed_file(filename, settings.EVENT_ALLOWED_EXTENSIONS):
            error = BadRequest()
            error.data = ['This file type is not allowed. Please contact admin.']
            raise error

        root_dir = os.getcwd()
        return send_from_directory(os.path.join(root_dir, settings.UPLOAD_FOLDER), filename)


app.add_url_rule('/download/<filename>', view_func=DownloadFile.as_view('download_file'))
