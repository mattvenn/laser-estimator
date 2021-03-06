from laser_estimator import app
from models import Material
from svgpathtools import svg2paths2
from flask_admin.contrib.sqla import ModelView
from flask import render_template, request, Response, flash, redirect, session, abort, url_for, send_from_directory
from werkzeug.utils import secure_filename
import logging
import os
import time
from flask_mail import Mail, Message
#from pprint import pprint

log = logging.getLogger()
log.setLevel(logging.DEBUG)
log_format = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(log_format)
log.addHandler(ch)

# inkscape conversion between px & mm
px_to_mm = 1 / 3.5433

# mail
mail = Mail(app)

from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, SelectField, PasswordField, TextField, HiddenField
from wtforms.validators import DataRequired, Email

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

class SendEmail(Form):
    name = StringField("Name",  [DataRequired("Please enter your name.")])
    email = StringField("Email",  [DataRequired("Please enter your email address."), Email("This field requires a valid email address")])
    material = HiddenField("material")
    cut_choices = HiddenField("cut_choices")
    svg = HiddenField("svg")
    email_total_cost = HiddenField("email_total_cost")

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

@app.route("/send_email", methods=['POST'])
def send_email():
    form = SendEmail()
    if form.validate_on_submit():
        log.info("sending email to %s" % app.config['EMAIL'])
        msg = Message("quote request", sender="samples@nice-cuts.com", recipients=[app.config['EMAIL']])
        root_dir = os.path.dirname(os.getcwd())
        image_path = os.path.join(root_dir, 'laser_estimator', form.svg.data)
        msg.body = "Name: %s\nEmail: %s\nMaterial: %s\nTotal Cost: %s\nCut choices: %s\n" % (form.name.data, form.email.data, form.material.data, form.email_total_cost.data, form.cut_choices.data)
        with app.open_resource(image_path) as fp:
            msg.attach(form.svg.data, "image/svg", fp.read())
        mail.send(msg)
    return render_template('send_email.html', form=form)

@app.route("/", methods=['GET', 'POST'])
def index():
    form = UploadSVG()
    form.material_id.choices = [(m.id, m) for m in Material.query.order_by('name')]
    if form.validate_on_submit():
        f = form.svg.data

        filename = secure_filename(f.filename)
        filename = os.path.join(app.config['UPLOAD_DIR'], secure_filename(f.filename))
        f.save(filename)
        filename_nomatrix = filename + ".nomatrix.svg"

        root_dir = os.path.dirname(os.getcwd())
        config = os.path.join(root_dir, 'laser_estimator', 'svgo.config')
        log.debug(config)

        # use svgo to cleanup svg files
        # might fail on dev machine as svgo is older
        os.system('svgo --pretty --config %s %s %s' % (config, filename, filename_nomatrix))

        # parse svg
        try:
            paths, attributes, svg_attributes = svg2paths2(filename_nomatrix)
            log.info("found %d paths in file" % len(paths))
        except Exception:
            flash('Problem parsing SVG file - make sure objects are converted to paths')
            return redirect('/')
            
        total_length = 0
        lengths_by_colour = {}
        total_paths = 0
        t_xmin, t_xmax, t_ymin, t_ymax = 1000000, -1000000, 1000000, -1000000 

        # quick check for outline path
        outline_ok = False
        for i in range(len(paths)):
            path = paths[i]
            attr = attributes[i]
            if attr.has_key('id'):
                if attr['id'] == 'OUTLINE':
                    log.debug("found outline path")
                    if abs(path.length() * px_to_mm - 2560) > 0.1:
                        flash('Problem with template, it has been resized.')
                        return redirect('/')
                    else:
                        outline_ok = True

        if not outline_ok:
            flash("Couldn't find template, please download it")
            return redirect('/')

        for i in range(len(paths)):
            colour = None
            path = paths[i]
            attr = attributes[i]

            # skip outline
            if attr.has_key('id'):
                if attr['id'] == 'OUTLINE':
                    continue

            if attr.has_key('stroke'):
                colour = attr['stroke']
            elif attr.has_key('style'):
                styles = attr['style'].split(';')
                for s in styles:
                    if s.startswith('stroke:'):
                        colour = s[7:] # just grab the colour
            if colour is None:
                log.debug("couldn't get colour for path, changing to black")

            # convert all black paths to the same style, so they don't show up twice
            if colour is None or colour == 'black' or colour == '#000000' or colour == 'rgb(0,0,0)':
                colour = '#000'

            log.debug("path %s length %s colour %s" % (total_paths, path.length() * px_to_mm, colour))
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

            log.debug("width = %d height = %d" % ((xmax - xmin) * px_to_mm, (ymax - ymin) * px_to_mm))

        material = Material.query.filter(Material.id == form.material_id.data).first()
        total_length_mm = total_length * px_to_mm
        log.info("total length = %f" % (total_length_mm))
        width = (t_xmax - t_xmin) * px_to_mm
        height = (t_ymax - t_ymin) * px_to_mm

        log.info("width = %d mm height = %d mm" % (width, height))
        # round up to nearest 50mm
        unit_size = app.config['UNIT_SIZE_MM']
        if total_paths == 0:
            width = 0
            height = 0
        else:
            width = (width + unit_size-1) // unit_size * unit_size 
            height = (height + unit_size-1) // unit_size * unit_size 

        log.info("rounded width = %d mm rounded height = %d mm" % (width, height))
        send_email_form = SendEmail()
        send_email_form.material.data = material
        send_email_form.svg.data = filename

        return render_template('estimation.html', 
            form=send_email_form,
            filename=filename,
            total_length=round(total_length, 2),
            total_length_mm=round(total_length_mm, 2),
            width=round(width, 2),
            height=round(height, 2),
            total_paths=total_paths,
            material=material,
            cut_cost=app.config['COST_PER_SEC'],
            material_cost=round(material.cost_per_unit * width * height / (unit_size * unit_size) ,2),
            lengths_by_colour = lengths_by_colour)

    return render_template('index.html', form=form)
