import itertools
import json
import math
import re
from io import BytesIO

from flask import Flask, jsonify, request, redirect, flash

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'json'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def document_phrase_frequency(phrase, documents):
    df = 0
    pf = 0
    for doc in documents:
        if len(doc.split()) > 0:
            if phrase in doc and len(phrase.strip().split(' ')) > 1:
                df = df + 1
                pf = pf + (doc.count(phrase) / float(len(doc.split())))

    df = df / float(len(documents))
    return df, pf

def ranking(M, documents):
    ranking = {}
    for seq in M:
        df, pf = document_phrase_frequency(seq, documents)
        ranking[seq] = pf * (-math.log(1 - df))

    sequence_sorted = sorted(ranking, key=ranking.get, reverse=True)[:50]
    final_phrases = filter(lambda x: [x for i in sequence_sorted if x in i and x != i] == [], sequence_sorted)
    return final_phrases

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
