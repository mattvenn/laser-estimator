import os
import unittest
from flask.ext.testing import TestCase
import config
from laser_estimator import app
from base64 import b64encode


class TestCase(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

    def test_svgs(self):
        config = [
            { 'file': '50x50_empty.svg', 'len': '200.0 mm' },
            { 'file': '50x50circle.svg', 'len': '156.98 mm' },
            { 'file': 'text_as_path.svg', 'len': '513.31 mm' },
            { 'file': '50x50_empty_RGB.svg', 'len': '600.0 mm' },
            ]
        
        for c in config:
            payload = { 'svg': open('testfiles/%s' % c['file']) }
            rv = self.client.post("/", data=payload)
            assert c['len'] in rv.data

if __name__ == '__main__':
    unittest.main()
