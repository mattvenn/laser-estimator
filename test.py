import os
import unittest
from flask.ext.testing import TestCase
import config
from tracker import app, db
from tracker.models import User
from base64 import b64encode


class TestCase(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

    def test_add_data(self):
        # first data
        payload = { 'file': open('testfiles/50x50empty.svg') }
        rv = self.client.post("/", data=payload)
        print rv.status_code


if __name__ == '__main__':
    unittest.main()
