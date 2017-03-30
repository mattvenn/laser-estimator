import os
import unittest
from flask.ext.testing import TestCase
import config
from laser_estimator import app, db, models
#import laser_estimator
from base64 import b64encode
import tempfile


class TestCase(TestCase):
    def create_app(self):
        return app

    def setUp(self):
       # self.app = app.test_client()
       # db.init_app(self.app)

        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = app.test_client()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.db_path
        app.config['WTF_CSRF_ENABLED'] = False
        db.create_all()
#            db.drop_all()
#            db.create_all()

        material = models.Material('ply', 3, 20, 10, 10)
        db.session.add(material)
        material = models.Material('acrylic', 5, 10, 5, 20)
        db.session.add(material)
        db.session.commit()

    def test_bounding_box(self):
        config = [
            { 'file': '50x50_empty.svg', 'bb': '50.0 x 50.0 mm' },
            { 'file': '50x50_empty_RGB.svg', 'bb': '200.0 x 100.0 mm' },
            { 'file': 'bounding.svg', 'bb': '200.0 x 150.0 mm' },
            ]
        for c in config:
            payload = { 'svg': open('testfiles/%s' % c['file']), 'material_id': 1}
            rv = self.client.post("/", data=payload)
            assert c['bb'] in rv.data

    def test_colour_paths(self):
        config = [
            { 'file': '50x50_empty.svg', 'col': 'colour #000 = 200.0 mm' },
            { 'file': '50x50_empty_RGB.svg', 'col': ' #00f = 200.0 mm' },
            { 'file': '50x50_empty_RGB.svg', 'col': ' #000 = 200.0 mm' },
            { 'file': '50x50_empty_RGB.svg', 'col': ' #f00 = 200.0 mm' },
            ]
        for c in config:
            payload = { 'svg': open('testfiles/%s' % c['file']), 'material_id': 1 }
            rv = self.client.post("/", data=payload)
            assert c['col'] in rv.data

    def test_svgs(self):
        config = [
            { 'file': '50x50_empty.svg', 'len': '200.0 mm', 'cost': '10.0' },
#            { 'file': '50x50circle.svg', 'len': '156.98 mm', 'cost': '10.0' }, # wrong! should be 50x50 and same price as square
            { 'file': 'text_as_path.svg', 'len': '513.31 mm', 'cost': '30.0' },
            { 'file': '50x50_empty_RGB.svg', 'len': '600.0 mm', 'cost': '80.0' },
            ]
        
        for c in config:
            payload = { 'svg': open('testfiles/%s' % c['file']), 'material_id': 1 }
            rv = self.client.post("/", data=payload, follow_redirects=True)
#            print rv.data
            assert c['len'] in rv.data
            assert c['cost'] in rv.data

    def test_material_list(self):
        rv = self.client.get("/", follow_redirects=True)
        assert 'ply - 3 mm' in rv.data
        assert 'acrylic - 5 mm' in rv.data

    def test_admin_no_pass(self):
        rv = self.client.get("/admin/material", follow_redirects=True)
        assert 'Login' in rv.data

    def test_admin_with_pass(self):
        rv = self.login(app.config['USERNAME'], app.config['PASSWORD'])
        rv = self.client.get("/admin/material", follow_redirects=True)
        assert 'sure you want to delete' in rv.data

    def login(self, username, password):
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)


if __name__ == '__main__':
    unittest.main()
