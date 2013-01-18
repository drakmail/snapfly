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

import os
from Queue import Queue
from subprocess import Popen
from debug import logINFO

devnull = open(os.path.devnull, 'w')
q = None
def start():
    global q
    q = Queue()

def stop():
    while not q.empty():
        q.get()
        q.task_done()
    q.join()

def check_programs():
    programs = []
    while not q.empty():
        program = q.get()
        if program.poll() == None:
            programs.append(program)
        q.task_done()
    for program in programs:
        q.put(program)
    return True

def launch_command(cmd):
    try:
        p = Popen(cmd, stdout = devnull, stderr = devnull )
        q.put(p)
    except OSError, e:
        logINFO("unable to execute a command: %s : %s" % (repr(cmd), repr(e) ))


