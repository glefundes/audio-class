import os
import json

def reset_annotation(session):
    if os.path.isfile(session['annot_fp']):
        os.remove(session['annot_fp'])
    accepted_formats = (".mp3", ".ogg")
    files = [
        {"file": file,
         "class":"",
         "obs": ""
         } for file in os.listdir(session['audio_dir'])  if file.endswith(accepted_formats)]
    classes = []
    session['annot'] = {"classes": classes, "files": files}
    session['file_idx'] = 0
    session.modified = True

def load_annot_to_session(annot, session):
    loaded_fnames = [f['file'] for f in annot['files']]
    session_fnames = [f['file'] for f in session['annot']['files']]
    if not all(fname in session_fnames for fname in loaded_fnames):
        return False, "json-with-missing-files"
    
    already_annotated = ([f for f in annot['files'] if f['class']!= ""])
    session['annot'] = annot
    session.modified = True
    return True, already_annotated

def save_json(session, savepath=None):
    savepath = savepath if savepath is not None else session['annot_fp']
    with open(savepath, 'w', encoding='utf-8') as f:
        json.dump(session['annot'], f, ensure_ascii=False, indent=4)
    return savepath