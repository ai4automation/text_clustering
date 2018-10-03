import os
from flask import Flask, request, redirect, url_for, send_from_directory, Response
from werkzeug import secure_filename
import event_cluster
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
  # this has changed from the original example because the original did not work for me
    return filename[-3:].lower() in ALLOWED_EXTENSIONS

def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))


def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(root_dir(), filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src).read()
    except IOError as exc:
        return str(exc)



@app.route('/cluster_events', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        comments_field = request.form.get('comments')
        action_field  = request.form.get('action')
        print("File: {}, Comments Field:{}, Event Field:{}".format(file.filename,comments_field,action_field))

        if file and allowed_file(file.filename):
            print('**found file {}'.format(file.filename))
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            derived_file = event_cluster.run_e2e(UPLOAD_FOLDER+"/"+filename,comments_field,action_field)
            # for browser, add 'redirect' function on top of 'url_for'
            return url_for('uploaded_file',filename=filename[:-4]+"_derived.csv")

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
