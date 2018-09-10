import json
from io import BytesIO
from flask import Flask, jsonify, request, redirect, flash
from utils.preprocess import preprocess
from utils.clustering import candidate_phrase, document_phrase_frequency, ranking

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'json'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def find_labels(byte_stream):
	cluster = {}
	comments = []
	total_candidates = []
	lookup = []
	data = json.loads(byte_stream)
	for comm in data:
		candidates = []
		preprocessed_comment, sentences = preprocess(comm)
		comments.append(preprocessed_comment)
		for sent in sentences:
			candidates.extend(candidate_phrase(sent))
		lookup[sent] = candidates
		total_candidates.extend(candidates)
	candidates = list(set(candidates))
	ranked_phrases = ranking(candidates, comments)
	for i in range(0,len(comments)):
		for phrase in ranked_phrases:
			if phrase in comments[i]:
				flag = 1
				if phrase in cluster:
					list_comm = cluster[phrase]
					list_comm.append(data[i])
					list_comm = list(set(list_comm))
					cluster[phrase] = list_comm
				else:
					cluster[phrase] = [data[i]]
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
