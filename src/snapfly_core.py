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
import locale
import gettext
import re
import shlex
import config

from .xdg import USERMENU, CONFIG_PATH
from debug import logINFO, logTRACEBACK, printERROR
from os.path import  expanduser, expandvars

#initializing gettext is already done in main snapfly script
_ = gettext.gettext

cat_name = {'Accessories': ['Utility', 'Accessories'],
            'Games': ['Game'],
            'Graphics': ['Graphics'],
            'Network': ['Internet', 'Network'],
            'Office': ['Office'],
            'Development': ['Development'],
            'Other': ['Other'],
            'Settings': ['Settings', 'X-XFCE'],
            'Multimedia': ['AudioVideo', 'Audio', 'Video', 'Multimedia'],
            'System': ['System', 'Administration'],
}

cat_icon = {'Accessories': 'applications-utilities',
            'Games': 'applications-games',
            'Graphics': 'applications-graphics',
            'Network': 'applications-internet',
            'Office': 'applications-office',
            'Other': 'applications-other',
            'Development': 'applications-development',
            'Settings': 'preferences-desktop',
            'Multimedia': 'applications-multimedia',
            'System': 'applications-system',
            'Favorites': 'emblem-favorite', # for standaloneness:
                                            # only one more more string
}
#if "FUCKING_FAVORITES" in os.environ:
# It's not place for troubling ConfigController

def hex2rgb(color_hex):
    ## convert Hex color to RGB
    hexcolor = color_hex.strip()[1:]
    if len(hexcolor) != 6:
        logINFO('Invalid hex color, use #RRGGBB format.')
        return 0.0, 0.0, 0.0
    hexcolor = int(hexcolor, 16)
    r, g, b = hexcolor >> 16, (hexcolor >> 8) & 255, hexcolor & 255
    return r / 255., g / 255., b / 255. # max is 0xff, trust me


# Get current locale with stripped .ENCODING part
def get_current_locale():
    cur_locale = locale.setlocale(locale.LC_MESSAGES, '')
    encoding_part = cur_locale.find(".")
    spec_part = cur_locale.find('@')
    if spec_part >= 0 and encoding_part >= 0:
        #Locale seems like en_US.utf8@latin
        cur_locale = cur_locale[:encoding_part] + cur_locale[spec_part:]
    elif encoding_part >= 0:
        #Locale seems like en_US.utf8
        cur_locale = cur_locale[:encoding_part]
        #Locale now seems like en_US or en_US@latin
    return cur_locale


def get_desktop_locale_variants():
    cur_locale = get_current_locale()
    locale_list = [cur_locale]
    spec_index = cur_locale.find('@')
    scope_index = cur_locale.find('_')
    if spec_index >= 0:
        #en_US@latin is in list
        #en_US
        locale_list.append(cur_locale[:spec_index])
        #en@latin
        if scope_index >= 0:
            locale_list.append(cur_locale[:scope_index] +
                               cur_locale[spec_index:])
            #else en_Us is in list
    if scope_index >= 0:
        locale_list.append(cur_locale[:scope_index])
    return locale_list


def get_i18n_name(name_locales):
    name = None
    current_locales = get_desktop_locale_variants()
    name_variants = {'C': None}
    for name_locale in name_locales:
        if name_locale == 'Name':
            name_variants['C'] = name_locales[name_locale]
        elif name_locale[5:-1] in current_locales:
            name_variants[name_locale[5:-1]] = name_locales[name_locale]

    for current_locale in current_locales:
        if current_locale in name_variants:
            name = name_variants[current_locale]
            break

    if name is None:
        name = name_variants['C']
    return name


def get_i18n_generic_name(generic_name_locales):
    generic_name = None
    current_locales = get_desktop_locale_variants()
    generic_name_variants = {'C': None}
    for generic_name_locale in generic_name_locales:
        if generic_name_locale == 'GenericName':
            generic_name_variants['C'] = generic_name_locales[generic_name_locale]
        elif generic_name_locale[12:-1] in current_locales:
            generic_name_variants[generic_name_locale[12:-1]] =\
            generic_name_locales[generic_name_locale]

    for current_locale in current_locales:
        if current_locale in generic_name_variants:
            generic_name = generic_name_variants[current_locale]
            break

    if generic_name is None:
        generic_name = generic_name_variants['C']
    return generic_name


def get_i18n_comment(comment_locales):
    comment = None
    current_locales = get_desktop_locale_variants()
    comment_variants = {'C': None}
    for comment_locale in comment_locales:
        if comment_locale == 'Comment':
            comment_variants['C'] = comment_locales[comment_locale]
            continue
        if comment_locale[8:-1] in current_locales:
            comment_variants[comment_locale[8:-1]] =\
            comment_locales[comment_locale]

    for current_locale in current_locales:
        if current_locale in comment_variants:
            comment = comment_variants[current_locale]
            break

    if comment is None:
        comment = comment_variants['C']
    return comment

REMOVE_F = re.compile('[^%]%[fFuUdDnNvm]')
PATH_F = re.compile('[^%]%k')
ICON_F = re.compile('[^%]%i')
#NAME_F = re.compile('[^%]%c')


def parse_cmd(cmd, filename, icon, name):
    cmd = REMOVE_F.sub('', cmd)
    cmd = PATH_F.sub(filename, cmd)
    cmd = ICON_F.sub('--icon ' + icon if icon else '', cmd)
    #cmd = NAME_F.sub(name, cmd)
    cmd = cmd.replace("%c", str(name))
    cmd = cmd.replace("%%", "%")
    cmd = shlex.split(cmd)
    return cmd


# Find the Name / Command / Icon from .desktop file
def info_desktop(filename, hideList, term_cmd=None):
    cmd = icon = name = comment = generic_name = None
    comment_locales, name_locales, generic_name_locales = {}, {}, {}
    category = 'Other'
    terminal = False
    #has_desktop_entry: если уже была секция с описанием .desktop файла - то дальше парсить .desktop файл нету
    #смысла. Если её еще не было - парсим дальше.
    has_desktop_entry = False
    try:
        cfile = open(filename, "r")
        for line in cfile:
            if line.startswith("[Desktop Entry]"):
                has_desktop_entry = True
            if "[Property::" in line:
                if has_desktop_entry:
                    break
            if line.startswith("[") and not line.startswith("[Desktop Entry]"):
                if has_desktop_entry:
                    break
            if '=' in line:
                key, value = line.strip().split('=', 1)
                if key == 'Type' and value != 'Application':
                    icon, category = None, None
                    break
                elif key == 'NoDisplay' and value == 'true':
                    icon, category = None, None
                    break
                elif key == 'OnlyShowIn':
                    showinlist = line.split(';')
                    hideList = set(hideList)
                    if not [item for item in showinlist if item not in hideList]:
                        # Original behaivour was strange; if we forbid GNOME
                        # and app is for GNOME and XFCE, we used to ban it.
                        # Todo: add support for NotShowIn.
                        icon, category = None, None
                        break
                elif key == 'Terminal' and value == 'true':
                    terminal = True
                elif key.startswith('Name'):
                    name_locales[key] = value
                elif key.startswith('Comment'):
                    comment_locales[key] = value
                elif key.startswith('GenericName'):
                    generic_name_locales[key] = value
                elif key == 'Icon' and value:
                    icon = value
                    if not icon[0] == '/':
                        icon = icon.split('.', 1)[0]
                if key == 'Exec':
                    cmd = value
                elif key == 'TryExec':
                    tryexec = config.PATH_search(value)
                    if tryexec is None:
                        icon, category = None, None
                        continue
                if key == 'Categories':
                    tab = value.split(';')

                    for cat in tab:
                        found = False
                        for c_name in cat_name:
                            if cat in cat_name[c_name]:
                                category = c_name
                                found = True
                                break
                        if found:
                            break

        name = get_i18n_name(name_locales)
        comment = get_i18n_comment(comment_locales)
        generic_name = get_i18n_generic_name(generic_name_locales)

        if cmd is not None:
            cmd = parse_cmd(cmd, filename, icon, name)

            # if command is 'console only', launch it with terminal ..
            if terminal:
                cmd = [term_cmd if term_cmd else 'xterm', '-e'] + cmd

        cfile.close()

        if comment is None:
            comment = generic_name
        
        if not category:
            category = 'Other'

        if category:
            logINFO("%s: %s->%s" % ( os.path.basename(filename), category, name ))
            return cmd, icon, name, category, comment

    except:
        logINFO(u"# Error : parsing %s" % filename)
        logTRACEBACK()
    return None


def parse_user_menu(config):
    logINFO('Parse user menu ..')
    cfg_file = USERMENU
    cat_index = None
    if os.access(cfg_file, os.F_OK | os.R_OK):
        logINFO('Found user menu ..')
        f = open(cfg_file, 'r')
        for line in f:
            try:
                if line == '\n' or line.startswith('#'):
                    continue
                elif line.startswith('@'):
                    if line.count("##") > 0:
                        cat = line[1:].strip('\n ').split("##")
                        config[cat[0]] = []
                        cat_icon[cat[0]] = expanduser( expandvars ( cat[1] ) )
                        cat_index = cat[0]
                    else:
                        printERROR(u"# Error reading line: %s, not enough parameters"
                              u" (must be at least 2)" % line)
                else:
                    if line.count("##") > 2:
                        if cat_index is not None:
                            #Parameters:#[0]CMD#[1]Icon#[2]Name#[3]--/--#[4]Desc
                            cmd_line = line.strip('\n\t ').split('##') 
                            cmd_line[0] = expanduser( expandvars ( cmd_line[0] ) )
                            cmd_line[1] = expanduser( expandvars ( cmd_line[1] ) )
                            cmd_line.insert(3, "")
                            cmd_line[0] = parse_cmd(cmd_line[0], "", cmd_line[1], cmd_line[2])
                            config[cat_index].append(cmd_line)
                        else:
                            printERROR( u"# Error reading line: %s, not enough parameters"
                                  u" (must be at least 3)" % line)
                    else:
                        printERROR( u"# Error reading line: %s, not enough parameters"
                              u" (must be at least 3)" % line)
            except:
                logINFO("# Error in user config menu at line: %s" % line)
                logTRACEBACK()
        f.close()
    return config


def parse_desktop_dir(term_cmd=None, hideList=None):
    menu_items = {}
    settings = config.ConfigController()
    logINFO('scan dir and parse .desktop file ..')
    blacklist = None
    desktop_dir = []
    blacklist_path = os.path.join(CONFIG_PATH, 'blacklist')
    if os.path.exists(blacklist_path):
        if os.path.isfile(blacklist_path):
            f = open(blacklist_path, "r")
            blacklist = filter(None, map(lambda l: l.strip().rstrip(), f.readlines()))
        elif os.path.isdir(blacklist_path):
            blacklist = filter(lambda l: l.endswith('.desktop'), os.listdir(blacklist_path))
    else:
        blacklist = []

    for dir_item in settings.getValue("desktop_dirs"):
        if os.path.exists(dir_item):
            desktop_dir.append(dir_item)

    for dir_item in desktop_dir:
        listdir = filter(lambda i: i.endswith('.desktop') and i not in blacklist, os.listdir(dir_item))
        logINFO ( listdir )
        for info in filter(None, map(lambda i: info_desktop(dir_item + i, hideList, term_cmd), listdir)):
            menu_items.setdefault(info[3], []).append(info)

    return menu_items


def create_favorites(term_cmd=None):
    term_cmd = term_cmd or 'xterm'
    candidates = [(term_cmd, 'terminal', _('Terminal'), 'Favorites', ''),
                  (os.getenv('BROWSER', 'x-www-browser'), 'web-browser',
                   _('Web Browser'), 'Favorites', ''),
                  (os.getenv('EMAIL_READER', 'xdg-email'), 'internet-mail',
                   _('Mail Composer'), 'Favorites', '')]
    res = []
    for candidate in candidates:
        if config.PATH_search(candidate[0]):
            res.append(candidate)
    return res

# Directly calling Thread.run results in nothing except direct call,
# so if it worked, it must work now.
class MakeMenu:
    def __init__ (self, callback_action, move_on_scroll_action,
                  terminal=None, hideList=None, showFavorites='false'):
        logINFO('MakeMenu ..')
        self.callback_action = callback_action
        self.move_on_scroll_action = move_on_scroll_action
        self.terminal = terminal
        self.hideList = hideList
        self.cat_visible = True
        self.showFavorites = showFavorites == 'true'

    def get_menu(self):
        """
        Parse .desktop files and return generated menu
        @return: menu (tuple of categories with items)
        """
        menu = parse_desktop_dir(term_cmd=self.terminal, hideList=self.hideList)
        menu = parse_user_menu(menu)
        return menu

    def get_favorites(self):
        """
        Return favorites list
        @return: favorites list
        """
        return create_favorites(term_cmd=self.terminal)