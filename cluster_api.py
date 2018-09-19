import json
from io import BytesIO
from flask import Flask, jsonify, request, redirect, flash
from utils.preprocess import get_n_grams
from utils.clustering import ranking, post_process

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'json'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def filter_unwanted(candidates):
	filtered = []
	unwanted= ["thank", "ibm", "please", "apologize", "dear", "sincerely","helpdesk", "better",
                "help-desk", "telephone", "regards", "phone", "regret", "gmail", "yahoo", "hotmail",
                "center", "exit", "time", "access", "administrator", "support", "assist", "skills",
                "proveitsupport", "contact"]
	for phrase in candidates:
		if not any(n in phrase for n in unwanted):
			filtered.append(phrase)
	return filtered

def find_labels(byte_stream):
	cluster = {}
	comments = []
	total_candidates = []
	lookup = {}
	comments = json.loads(byte_stream)
	comments = list(set(comments))
	print(len(comments))
	mapping_preprocess, mapping_ngrams, candidates = get_n_grams(comments)
	#print(candidates)
	#print(mapping_ngrams)
	#print("filtered: ", filter_unwanted(list(set(candidates))))
	ranked_phrases, score_dict = ranking(filter_unwanted(list(set(candidates))),comments, mapping_preprocess)
	#print(ranked_phrases)
	final_list = post_process(ranked_phrases, score_dict, comments, mapping_preprocess)
	print(final_list)
	lookup_comments = [k for k in comments if len(list(set(mapping_ngrams[k]) & set(final_list)))==0]
	for comm in lookup_comments:
		candidates_lookup = mapping_ngrams[comm]
		if len(candidates_lookup)>0:
                        ranked_lookup, score_lookup = ranking(filter_unwanted(list(set(candidates_lookup))), comments, mapping_preprocess)
                        if len(ranked_lookup)>0:
                        	final_list.append(ranked_lookup[0])
	final_list = list(set(final_list))
	print("final list: ", final_list)
	uncommented = 0
	for i in range(0,len(comments)):
		flag = 0
		for phrase in final_list:
			if phrase in mapping_preprocess[comments[i]]:
				flag = 1
				if phrase in cluster:
					list_comm = cluster[phrase]
					list_comm.append(comments[i])
					list_comm = list(set(list_comm))
					cluster[phrase] = list_comm
				else:
					cluster[phrase] = [comments[i]]
		if flag == 0:
			uncommented +=1
	print(uncommented)
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
