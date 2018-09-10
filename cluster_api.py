import json
from io import BytesIO
from flask import Flask, jsonify, request, redirect, flash

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'json'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def find_labels(byte_stream):
	cluster = {}
	data = json.loads(byte_stream)
	return cluster

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file__ = request.files.get('file')
        # if user does not select file, browser also
        # submit a empty part without filename
        if file__.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file__ and allowed_file(file__.filename):
            mem_file = BytesIO()
            file__.save(mem_file)
            output = find_labels(mem_file.getvalue().decode('UTF-8'))
            response = jsonify(output)
            response.status_code = 201
            return response

        else:
            response = jsonify({'error': 'Some error! Please contact admin.'})
            response.status_code = 500
            return response

    return '''
            <!doctype html>
            <title>Convert</title>
            <h1>Upload new file to convert</h1>
            <form method=post enctype=multipart/form-data>
              <p><input type=file name=file>
                 <input type=submit value=Upload>
            </form>
            '''

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='0.0.0.0', debug=True, port=3000)
