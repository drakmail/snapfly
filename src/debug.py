#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2010-2011
#   Drakmail < drakmail@gmail.com >
#   NomerUNO < uno.kms@gmail.com >
#   Platon Peacel☮ve <platonny@ngs.ru>
#   Elec.Lomy.RU <Elec.Lomy.RU@gmail.com>
#   ADcomp <david.madbox@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

## Only for debugging : False / True
from os import getenv
from os.path import  expanduser, expandvars
import sys, codecs
from threading import Semaphore
from traceback import print_exc

DEBUG = True if getenv("SNAPDEBUG") is not None else False
_debug_file = None

if DEBUG:
    sem = Semaphore(1)
    SNAPDEBUG = getenv("SNAPDEBUG")
    if SNAPDEBUG:
        _debug_file_path = expanduser( expandvars ( SNAPDEBUG ) )
        _debug_file = codecs.open(_debug_file_path, "w", "utf8")
        del _debug_file_path, SNAPDEBUG

def logINFO(msg, from_mod=""):
    if DEBUG:
        sem.acquire()
        try:
            if type(msg) in (str, unicode):
                message = u"[SnapFly.%s] %s\n" % (from_mod, msg)
            else:
                message = u"[SnapFly.%s] %s\n" % (from_mod, repr(msg))
            if _debug_file:
                _debug_file.write( message )
                _debug_file.flush()
            else:
                sys.stderr.write( message )
        except:
            pass
        sem.release()

def logTRACEBACK():
    if DEBUG:
        sem.acquire()
        print_exc(sys.stdout if not _debug_file else _debug_file )
        sem.release()

def printERROR(message):
    if DEBUG:
        if _debug_file:
            sys.stderr.write( message + u"\n" )
        logINFO(message)
    else:
        sys.stderr.write( message + u"\n" )

