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
from .xdg import CONFIG_FILE
from debug import logINFO, printERROR
from os.path import  expanduser, expandvars

def PATH_search(name):
    '''Search binary for PATH.'''
    if os.path.basename(name) != name:
        fullpath = [name]
    else:
        fullpath = [os.path.join(path, name)
                    for path in os.getenv('PATH', '').split(':')]
    for path in fullpath:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return os.path.abspath(path)
    else:
        return None

#TODO: Сделать его синглетоном (http://ru.wikipedia.org/wiki/%D0%A1%D0%B8%D0%BD%D0%B3%D0%BB%D1%82%D0%BE%D0%BD_%28%D1%88%D0%B0%D0%B1%D0%BB%D0%BE%D0%BD_%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F%29)
class ConfigController():
    def __init__(self):
        if PATH_search('x-terminal-emulator'):
            terminal = 'x-terminal-emulator'
        else:
            terminal = 'xterm'
        self.default = {'terminal': terminal,
                        'systray': 'true',
                        'rounded': '4',
                        'menu_width': '430',
                        'bg_color': '#DCDCDC',
                        'border_color': '#4D4D4D',
                        'hide_list': 'None',
                        'category_click': 'true',
                        'favorites': 'false',
                        'desktop_dirs': ["/usr/share/applications/",
                                        "%s/.local/share/applications/"
                                        % os.getenv('HOME'),
                                        "/usr/local/share/applications/",
                                        "/usr/share/applications/kde4/",
                                        "/usr/local/share/applications/kde4/"
                                        ]
                        }
        config = {}
        try:
            f = open(CONFIG_FILE, 'r')
            logINFO("Found user config.")
            for line in f:
                if line == '\n' or line.startswith('#'):
                    continue
                else:
                    line = line.strip('\n ').split('=')
                    if line[0] == "desktop_dirs":
                        config["desktop_dirs"] = filter( None, 
                                      map ( lambda ln: expanduser( expandvars ( ln.lstrip().rstrip() ) ),
                                           line[1].split(",") ) 
                                     )
                    else:
                        config[line[0]] = line[1]
            f.close()
        except IOError,e:
            printERROR(u"I/O error: %s" % repr(e))
        except Exception, e:
            printERROR( u"Error reading config file: %s" % repr(e))
        self.config = config
        self.validateConfig()

    #Check, if string is _valid_ integer.
    def isValidInt(self, string):
        try:
            int(string.strip().split()[0])
        except (ValueError, IndexError):
            return False
        return True

    def validateConfig(self):
        for line in self.config:
            if line not in self.default:
                printERROR( u"Error in config file: Unknown parameter (\"{0}\")".format(line))
                continue
            if self.config[line] == '':
                printERROR(u"Error in config file: parameter \"{0}\" can't be empty. Using default value.".format(line))
                self.config[line] = self.default[line]
            if line == 'rounded' or line == 'menu_width':
                if not self.isValidInt(self.config[line]):
                    printERROR( u"Error in config file: parameter \"{0}\" must be valid integer. Using default value.".format(line))
                    self.config[line] = self.default[line]
                if int(self.config[line]) < 0:
                    printERROR(u"Error in config file: parameter \"{0}\" must be positive value. Using default value.".format(line))
                    self.config[line] = self.default[line]

    def getValue(self, parameter):
        if parameter in self.config:
            return self.config[parameter]
        else:
            return self.default[parameter]
