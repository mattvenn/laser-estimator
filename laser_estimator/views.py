from laser_estimator import app
from models import Material
from svgpathtools import svg2paths2
from flask_admin.contrib.sqla import ModelView
from flask import render_template, request, Response, flash, redirect, session, abort, url_for, send_from_directory
from werkzeug.utils import secure_filename
import logging
import os
import time
#from pprint import pprint

log = logging.getLogger()
log.setLevel(logging.INFO)
log_format = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(log_format)
log.addHandler(ch)

# inkscape conversion between px & mm
px_to_mm = 1 / 3.5433

from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, SelectField, PasswordField, TextField
from wtforms.validators import DataRequired

"""    

    except Exception:
        user.bad_uploads +=1
        db.session.commit()
        log.warning("problem parsing file")
        abort(500)
"""

class SecureView(ModelView):
    def is_accessible(self):
        if 'logged_in' in session.keys():
            return True

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

class LoginForm(Form):
    username = TextField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.username.data != app.config['USERNAME']:
            self.username.errors.append('Unknown username')
            time.sleep(1)
            return False

        if self.password.data != app.config['PASSWORD']:
            self.password.errors.append('bad password')
            time.sleep(1)
            return False

        return True



class UploadSVG(Form):
    svg = FileField('svg', validators=[DataRequired()])
    material_id = SelectField(u'Material', coerce=int)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['logged_in'] = True
        flash('You were logged in')
        return redirect('/admin')
    return render_template('login.html', form=form)


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
    form.material_id.choices = [(m.id, m) for m in Material.query.order_by('name')]
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
        lengths_by_colour = {}
        total_paths = 0
        t_xmin, t_xmax, t_ymin, t_ymax = 1000000, 0, 1000000, 0
        for i in range(len(paths)):
            colour = None
            path = paths[i]
            attr = attributes[i]
            style = attr['style']
            styles = style.split(';')
            for s in styles:
                if s.startswith('stroke:'):
                    colour = s[7:] # just grab the colour
            #pprint(path)
            #pprint(styles)
            log.info("path %d id %s length %d colour %s" % (total_paths, attr['id'], path.length(), colour))
            try:
                lengths_by_colour[colour] += round(path.length() * px_to_mm, 2)
            except KeyError:
                lengths_by_colour[colour] = round(path.length() * px_to_mm, 2)
            
            total_length += path.length()
            total_paths += 1

            # bounding box
            xmin, xmax, ymin, ymax = path.bbox()
            if xmin < t_xmin:
                t_xmin = xmin
            if xmax > t_xmax:
                t_xmax = xmax
            if ymin < t_ymin:
                t_ymin = ymin
            if ymax > t_ymax:
                t_ymax = ymax

            #log.info("width = %d height = %d" % ((xmax - xmin) * px_to_mm, (ymax - ymin) * px_to_mm))

        material = Material.query.filter(Material.id == form.material_id.data).first()
        total_length_mm = total_length * px_to_mm
        log.info("total length = %d" % (total_length_mm))
        width = (t_xmax - t_xmin) * px_to_mm
        height = (t_ymax - t_ymin) * px_to_mm
        log.info("width = %d mm height = %d mm" % (width, height))

        return render_template('estimation.html', 
            filename=filename,
            total_length=round(total_length, 2),
            total_length_mm=round(total_length_mm, 2),
            width=round(width, 2),
            height=round(height, 2),
            total_paths=total_paths,
            material=material,
            cut_cost=app.config['COST_PER_SEC'],
            material_cost=round(material.cost_per_unit * width * height / 10000,2),
            lengths_by_colour = lengths_by_colour)

    return render_template('index.html', form=form)
