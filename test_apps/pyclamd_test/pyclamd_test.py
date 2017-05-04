#!/usr/bin/env python

import pyclamd
cd = pyclamd.ClamdAgnostic()
print "Asking to scan Stream w/ EICAR: "
print cd.scan_stream(cd.EICAR())

