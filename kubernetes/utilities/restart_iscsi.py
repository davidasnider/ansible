#!/usr/bin/env python

import sys
from helper import freenas_service_restart

freenas_service_restart("iscsitarget")
