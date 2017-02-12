from laser_estimator import app
from svgpathtools import svg2paths2
from flask import render_template, request, Response, flash, redirect, session, abort, url_for, send_from_directory
from werkzeug.utils import secure_filename
import logging
import os
from applytransform import ApplyTransform

log = logging.getLogger()
log.setLevel(logging.INFO)
log_format = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(log_format)
log.addHandler(ch)

# inkscape conversion between px & mm
px_to_mm = 1 / 3.5433
laser_cut_spd = 5 * 60 # mm per minute

from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

"""    

    except Exception:
        user.bad_uploads +=1
        db.session.commit()
        log.warning("problem parsing file")
        abort(500)
"""

class UploadSVG(Form):
    svg = FileField('svg', validators=[DataRequired()])

@app.route('/uploads/<path:path>')
def static_file(path):
    root_dir = os.path.dirname(os.getcwd())
    directory = os.path.join(root_dir, 'laser_estimator', app.config['UPLOAD_DIR'])
    log.info(directory)
    log.info(path)
#    import ipdb; ipdb.set_trace()
    #directory = '/home/matthew/work/python/laser-estimator/laser-estimator/uploads/' #50x50circle.scoured.svg
    return send_from_directory(directory, path)

@app.route("/", methods=['GET', 'POST'])
def index():
    form = UploadSVG()
    if form.validate_on_submit():
        f = form.svg.data

        filename = secure_filename(f.filename)
        filename = os.path.join(app.config['UPLOAD_DIR'], secure_filename(f.filename))
        f.save(filename)
        filename_nomatrix = filename + ".nomatrix"


        # couldn't get the inkscape plugin to run within this context, so running as a process ;(
        os.system('python applytransform.py %s > %s' % (filename, filename_nomatrix))

        # parse svg
        paths, attributes, svg_attributes = svg2paths2(filename_nomatrix)
        log.info("found %d paths in file" % len(paths))

        total_length = 0
        total_paths = 0
        for i in range(len(paths)):
            path = paths[i]
            attr = attributes[i]
        #    pprint(path)
        #    pprint(attr)
            log.info("path %d id %s length %d" % (total_paths, attr['id'], path.length()))
            total_length += path.length()
            total_paths += 1

        total_length_mm = total_length * px_to_mm
        log.info("total length = %d" % (total_length_mm))

        return render_template('estimation.html', 
            filename=filename,
            total_length=round(total_length,2),
            total_length_mm=round(total_length_mm,2),
            total_paths=total_paths,
            time=round(total_length_mm/laser_cut_spd,2))

    return render_template('index.html', form=form)
