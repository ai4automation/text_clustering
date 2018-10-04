from flask_restplus import reqparse
from werkzeug.datastructures import FileStorage

# text clustering parser
cluster_parser = reqparse.RequestParser()
cluster_parser.add_argument('file', location='files', type=FileStorage, required=True, help='JSON file to cluster')
cluster_parser.add_argument('n', required=True, help='Maximum word length for cluster labels', type=int)
cluster_parser.add_argument('coverage', default='false', choices=['true', 'false'], help='Maximum coverage')

# event comment clustering parser
event_parser = reqparse.RequestParser()
event_parser.add_argument('file', location='files', type=FileStorage, required=True, help='CSV logfile')
event_parser.add_argument('comments', required=True, help='Comment field name in logfile')
event_parser.add_argument('action', required=True, help='Event field name in logfile')
