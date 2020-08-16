import os
import json 

from app import app
from flask import render_template, session,\
                  request, redirect,\
                  url_for, send_from_directory,\
                  send_file

from werkzeug.utils import secure_filename
import app.utils as utils

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index(): 
    audio_dir = os.path.join(os.path.dirname(app.root_path),'audio_data')
    if not os.path.isdir(audio_dir):
        os.mkdir(audio_dir)
    session['annot_fp'] = os.path.join(os.path.dirname(app.root_path), '.temp.json')
    session['audio_dir'] = audio_dir
    session.modified = True

    utils.reset_annotation(session)
    num_files = len(session['annot']['files'])
    return render_template('index.html', title='Home', num_files=num_files)

@app.route('/annotate')
def annotate():    
    if len(session['annot']['files']) == 0:
        return ("no-files", 400)
    elif len(session['annot']['classes']) < 2 :
        return ("not-enough-classes", 400)

    else:
        return (render_template('annotate.html', annot=session['annot'], file_idx=session['file_idx']), 200)

@app.route('/upload_annotation', methods=["GET", "POST"])
def upload_annotation():
    if request.method == 'POST':
        if request.files['file']:
            f = request.files['file']
            fname = secure_filename(f.filename)
            if fname.endswith('.json'):
                f.save(fname)
                try:
                    with open(fname, 'r') as j:
                        json_file = json.load(j)
                except:
                    return ('invalid-json-file', 400)
                os.rename(fname, session['annot_fp'])
                loaded, msg = utils.load_annot_to_session(json_file, session)
                if loaded:
                    already_annotated = msg # Future use in player filtering
                    return (render_template('session_info.html', annot=session['annot'], annotated=len(already_annotated)), 200)
                else:
                    return (msg, 400)
            else:
                return ('invalid-json-file', 400)                

@app.route('/setup', methods=['GET'])
def setup_classes():
    classes = session['annot']['classes']
    action = request.args.get('action')

    if action == 'add':
        new_class = request.args.get('payload')
        classes = session['annot']['classes']
        # Duplicate class
        if new_class in [c['class_label'] for c in classes]:
            return ('duplicate-class', 400)
        if new_class == "":
            return ('empty-class', 400)
        classes.append({'index': len(classes), 'class_label': new_class})
        session['annot']['classes'] = classes       
        session.modified = True

    elif action == 'remove':
        to_remove_index = request.args.get('payload')
        classes = [c for c in session['annot']['classes'] if c['index'] != int(to_remove_index)]
        classes = [{'index': i, 'class_label': c['class_label']} for i, c in enumerate(classes)]
        session['annot']['classes'] = classes
        session.modified = True
        return (render_template('class_table.html', classes=classes), 200)

    elif action == 'reset':
        classes = []
        session['annot']['classes'] = classes
        session.modified = True

    elif action == 'start':
        return redirect(url_for('annotate'))
    
    return (render_template('class_table.html', classes=classes), 200)

@app.route('/iterate_files', methods=['POST'])
def iterate_files():
    hide_annotated = bool(request.form['hide-annotated'] == 'true')
    if hide_annotated:
        files = [f for f in session['annot']['files'] if f['class'] == ""]
    else:
        files = session['annot']['files']

    action = request.form['action']
    if action == 'next':
        if session['file_idx'] != len(files)-1:
            session['file_idx']  += 1

    elif action == 'prev':
        if session['file_idx'] != 0:
            session['file_idx']  -= 1

    elif action == 'first':
        session['file_idx'] = 0
    
    elif action == 'last':
        session['file_idx'] = len(files)-1

    else:
        session['file_idx'] = 0

    file_idx = session['file_idx']
    session.modified = True
    return render_template('player.html', files=files, file_idx=file_idx) 

@app.route('/download_annotation', methods=["GET"])
def download_annotation():
    tmp_json = utils.save_json(session)
    return send_file(tmp_json, as_attachment=True, mimetype='application/json', attachment_filename="annotation.json")

@app.route('/sounds/<path:filename>')
def fetch_soundfile(filename):
    return send_from_directory(session['audio_dir'], filename)

@app.route('/submit_annotation', methods=['POST'])
def submit_annotation():
    data = request.form
    filename = data['filename']
    hide_annotated = data['meta[hide-annotated]']

    file_idx = next(index for (index, d) in enumerate(session['annot']['files']) if d["file"] == filename)
    session['annot']['files'][file_idx]['class'] = int(data['class_idx'])
    session['annot']['files'][file_idx]['obs'] = data['obs']   

    if bool(hide_annotated == 'true'):
        files = [f for f in session['annot']['files'] if f['class'] == ""]
        if session['file_idx'] > len(files)-1:
            session['file_idx'] = len(files)-1
    else:
        files = session['annot']['files']
        if session['file_idx'] != len(files)-1:
            session['file_idx'] += 1

    session.modified = True
    return render_template('player.html', files=files, file_idx=session['file_idx'])
    # return ('', 204)