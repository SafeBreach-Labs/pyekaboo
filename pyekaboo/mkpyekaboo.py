#!/usr/bin/env python
#
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
import argparse
import pyekaboo
import inspect

####################
# Global Variables #
####################

__version__ = "1.0"
__author__ = "Itzik Kotler"
__copyright__ = "Copyright 2017, SafeBreach"

START_OF_CODE = "### DO NOT REMOVE THIS LINE! ###"
START_OF_CODE_LEN = 32


###########
# Classes #
###########

# http://stackoverflow.com/questions/3853722/python-argparse-how-to-insert-newline-in-the-help-text

class SmartFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('ML|'):
            return text[3:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


#############
# Functions #
#############

def main(args):
    parser = argparse.ArgumentParser(prog='mkpyekaboo', description='Python Hooking Library and Tool', formatter_class=SmartFormatter)
    parser.add_argument('pymodule', metavar='PYTHON_MODULE_NAME', type=str, help='Python module to be hooked (e.g. string, os, etc.)')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
    parser.add_argument('-l', '--hook-level', type=int, default=0, metavar='HOOK_LEVEL', help='ML|Level 0: Empty Pyekaboo Boilerplate (Default)\nLevel 1: Hook all Python Classes in PYTHON_MODULE_NAME\nLevel 2: Hook all Python Functions in PYTHON_MODULE_NAME\nLevel 3: Hook all Python Classes & Functions in PYTHON_MODULE_NAME\nLevel 4: Hook all Python Classes in PYTHON_MODULE_NAME and Enable Trace\nLevel 5: Hook all Python Functions in PYTHON_MODULE_NAME and Enable Trace\nLevel 6: Hook all Python Classes & Functions in PYTHON_MODULE_NAME and Enable Trace')
    args = parser.parse_args(args=args[1:])
    mod = None
    tot_hooked_classes = 0
    tot_hooked_fcns = 0

    with open(args.pymodule + '.py', 'w') as outfile:

        if args.verbose:
            print "Output Filename: %s" % outfile

        buf = open(pyekaboo.__file__.replace('pyc', 'py'), 'r').read()
        outfile.write(buf[buf.find(START_OF_CODE)+START_OF_CODE_LEN:].strip())
        outfile.write('\n\n###############\n# Entry Point #\n###############\n\n')

        if args.verbose:
            print "Wrote Pykeaboo Library (%d bytes)" % len(buf)

        # Hook all Classes (and maybe Enable Trace?)
        if args.hook_level == 1 or args.hook_level == 3 or args.hook_level == 4 or args.hook_level == 6:
            if args.verbose:
                print "Hooking Classes (hook_level == %d)" % args.hook_level

            mod = pyekaboo._load_and_register_as(args.pymodule, [args.pymodule], sys.path[::-1])

            if args.verbose:
                print "Imported %s as %s ..." % (args.pymodule, mod)

            for cls_name in dir(mod):
                if args.verbose:
                    print "Is %s a Class ... " % (cls_name),

                cls_obj = getattr(mod, cls_name)

                # TODO: Need a better way to handle cases where class is not really a class (i.e. socket.MethodType)
                if inspect.isclass(cls_obj) is True and repr(cls_obj).find("class") != -1:
                    # class _fileobject():
                    #    __metaclass__ = _InstallClsHook
                    #    __trace__ = True?
                    outfile.write('class ' + cls_name + '():\n')
                    outfile.write('    __metaclass__ = _InstallClsHook\n')
                    if args.hook_level == 4 or args.hook_level == 6:
                        outfile.write('    __trace__ = True\n')
                    outfile.write('\n')
                    tot_hooked_classes = tot_hooked_classes + 1
                    if args.verbose:
                        print "Yes! (%s)" % cls_obj
                else:
                    if args.verbose:
                        print "No"

        print "[*] Hooked %d Classes!" % tot_hooked_classes

        # Hook all Functions (and maybe Enable Trace?)
        if args.hook_level == 2 or args.hook_level == 3 or args.hook_level == 5 or args.hook_level == 6:
            mod = pyekaboo._load_and_register_as(args.pymodule, [args.pymodule], sys.path[::-1])

            if args.verbose:
                print "Imported %s as %s ..." % (args.pymodule, mod)

            for fcn_name in dir(mod):
                if args.verbose:
                    print "Is %s a Function ... " % (fcn_name),

                fcn_obj = getattr(mod, fcn_name)

                if inspect.isfunction(fcn_obj) is True or inspect.isroutine(fcn_obj) is True:
                    dbg_flag = "False"
                    if args.hook_level == 5 or args.hook_level == 6:
                        dbg_flag = "True"
                    # gethostbyname = _InstallFcnHook(gethostbyname, debug=True)
                    outfile.write('\n%s=_InstallFcnHook(%s, debug=%s)\n' % (fcn_name, fcn_name, dbg_flag))
                    tot_hooked_fcns = tot_hooked_fcns + 1
                    if args.verbose:
                        print "Yes! (%s)" % fcn_obj
                else:
                    if args.verbose:
                        print "No"

        print "[*] Hooked %d Functions!" % tot_hooked_fcns

if __name__ == "__main__":
    sys.exit(main(sys.argv))

