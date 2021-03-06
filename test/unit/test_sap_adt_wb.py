#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, PropertyMock

from sap.errors import SAPCliError
import sap.adt.wb

from mock import Connection, Response
from fixtures_adt import EMPTY_RESPONSE_OK
from fixtures_adt_wb import ACTIVATION_REFERENCES_XML, INACTIVE_OBJECTS_XML, PREAUDIT_ACTIVATION_XML


FIXTURES_EXP_FULL_ADT_URI = '/unit/test/mobject'
FIXTURES_EXP_OBJECT_NAME = 'MOBJECT'

FIXTURES_ACTIVATION_REQUEST_SINGLE = f'''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="{FIXTURES_EXP_FULL_ADT_URI}" adtcore:name="{FIXTURES_EXP_OBJECT_NAME}"/>
</adtcore:objectReferences>'''
FIXTURES_EXP_ERROR_RESPONSE = '<?xml version="1.0" encoding="utf-8"><error>failure</error>'


class TestADTWBActivate(unittest.TestCase):

    def create_fake_object(self, full_adt_uri, name, responses=None):
        conn = Connection(responses=responses)

        adt_object = Mock()
        adt_object.full_adt_uri = full_adt_uri
        adt_object.name = name
        adt_object.connection = conn

        return adt_object

    def assert_single_request(self, fake_adt_object):
        conn = fake_adt_object.connection

        self.assertEqual(conn.mock_methods(), [('POST', '/sap/bc/adt/activation')])

        self.assertEqual(sorted(conn.execs[0].headers),  ['Accept', 'Content-Type'])
        self.assertEqual(conn.execs[0].headers['Accept'], 'application/xml')
        self.assertEqual(conn.execs[0].headers['Content-Type'], 'application/xml')

        self.assertEqual(sorted(conn.execs[0].params),  ['method', 'preauditRequested'])
        self.assertEqual(conn.execs[0].params['method'], 'activate')
        self.assertEqual(conn.execs[0].params['preauditRequested'], 'true')

        self.maxDiff = None
        self.assertEqual(conn.execs[0].body, FIXTURES_ACTIVATION_REQUEST_SINGLE)

    def test_adt_wb_activate_object_ok(self):
        # user lower case name
        adt_object = self.create_fake_object(FIXTURES_EXP_FULL_ADT_URI, FIXTURES_EXP_OBJECT_NAME.lower())
        sap.adt.wb.activate(adt_object)
        self.assert_single_request(adt_object)

        # user upper case name
        adt_object = self.create_fake_object(FIXTURES_EXP_FULL_ADT_URI, FIXTURES_EXP_OBJECT_NAME.upper())
        sap.adt.wb.activate(adt_object)
        self.assert_single_request(adt_object)

    def test_adt_wb_activate_object_fail(self):
        adt_object = self.create_fake_object(FIXTURES_EXP_FULL_ADT_URI, FIXTURES_EXP_OBJECT_NAME)
        adt_object.connection = Connection([Response(status_code=200,
                                                     text=FIXTURES_EXP_ERROR_RESPONSE,
                                                     headers={})])

        with self.assertRaises(SAPCliError) as caught:
            sap.adt.wb.activate(adt_object)

        self.assert_single_request(adt_object)
        self.assertEqual(str(caught.exception),
                         f'Could not activate the object {FIXTURES_EXP_OBJECT_NAME}: {FIXTURES_EXP_ERROR_RESPONSE}')

    def test_adt_wb_activate_children(self):
        adt_object = self.create_fake_object('/sap/bc/adt/oo/classes/cl_hello_world',
                                             'cl_hello_world',
                                             [Response(status_code=200,
                                                       text=INACTIVE_OBJECTS_XML,
                                                       headers={'Content-Type': 'application/vnd.sap.adt.inactivectsobjects.v1+xml'}),
                                              EMPTY_RESPONSE_OK])

        sap.adt.wb.activate(adt_object)

        conn = adt_object.connection

        self.assertEqual(conn.mock_methods(), [('POST', '/sap/bc/adt/activation')] * 2)

        self.assertEqual(sorted(conn.execs[0].headers),  ['Accept', 'Content-Type'])
        self.assertEqual(conn.execs[0].headers['Accept'], 'application/xml')
        self.assertEqual(conn.execs[0].headers['Content-Type'], 'application/xml')

        self.assertEqual(sorted(conn.execs[0].params),  ['method', 'preauditRequested'])
        self.assertEqual(conn.execs[0].params['method'], 'activate')
        self.assertEqual(conn.execs[0].params['preauditRequested'], 'true')

        self.assertEqual(sorted(conn.execs[1].headers),  ['Accept', 'Content-Type'])
        self.assertEqual(conn.execs[1].headers['Accept'], 'application/xml')
        self.assertEqual(conn.execs[1].headers['Content-Type'], 'application/xml')

        self.assertEqual(sorted(conn.execs[1].params),  ['method', 'preauditRequested'])
        self.assertEqual(conn.execs[1].params['method'], 'activate')
        self.assertEqual(conn.execs[1].params['preauditRequested'], 'false')

        self.maxDiff = None
        self.assertEqual(conn.execs[0].body, PREAUDIT_ACTIVATION_XML)
        self.assertEqual(conn.execs[1].body, ACTIVATION_REFERENCES_XML)


if __name__ == '__main__':
    unittest.main()
