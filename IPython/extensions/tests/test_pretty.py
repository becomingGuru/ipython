#!/usr/bin/env python
# encoding: utf-8
"""
Simple tests for :mod:`IPython.extensions.pretty`.
"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2008-2009  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

from unittest import TestCase

from IPython.core.component import Component, masquerade_as
from IPython.core.iplib import InteractiveShell
from IPython.extensions import pretty as pretty_ext
from IPython.external import pretty
from IPython.testing import decorators as dec
from IPython.testing import tools as tt
from IPython.utils.traitlets import Bool

#-----------------------------------------------------------------------------
# Tests
#-----------------------------------------------------------------------------

class InteractiveShellStub(Component):
    pprint = Bool(True)

class A(object):
    pass

def a_pprinter(o, p, c):
    return p.text("<A>")

class TestPrettyResultDisplay(TestCase):

    def setUp(self):
        self.ip = InteractiveShellStub(None)
        # This allows our stub to be retrieved instead of the real
        # InteractiveShell
        masquerade_as(self.ip, InteractiveShell)
        self.prd = pretty_ext.PrettyResultDisplay(self.ip,
                                                  name='pretty_result_display')

    def test_for_type(self):
        self.prd.for_type(A, a_pprinter)
        a = A()
        result = pretty.pretty(a)
        self.assertEquals(result, "<A>")

ipy_src = """
class A(object):
    def __repr__(self):
        return 'A()'
    
class B(object):
    def __repr__(self):
        return 'B()'
 
a = A()
b = B()

def a_pretty_printer(obj, p, cycle):
    p.text('<A>')

def b_pretty_printer(obj, p, cycle):
    p.text('<B>')


a
b

ip = get_ipython()
prd = ip.load_extension('pretty')
prd.for_type(A, a_pretty_printer)
prd.for_type_by_name(B.__module__, B.__name__, b_pretty_printer)

a
b
"""
ipy_out = """
A()
B()
<A>
<B>
"""

class TestPrettyInteractively(tt.TempFileMixin):
    
    # XXX Unfortunately, ipexec_validate fails under win32.  If someone helps
    # us write a win32-compatible version, we can reactivate this test.
    @dec.skip_win32
    def test_printers(self):
        self.mktmp(ipy_src, '.ipy')
        tt.ipexec_validate(self.fname, ipy_out)
