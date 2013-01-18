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

import gtk
import sys

try:
    from config import ConfigController
    import snapfly_core
    from gui import GtkMenu
    from gui import TrayIcon
    from version import Application
    from launcher import launch_command
except ImportError:
    sys.stderr.write("Can't import snapfly menu modules.\nExiting\n")
    import traceback

    traceback.print_exc(sys.stderr)
    sys.exit(1)

class Menu:
    def __init__(self, notifier, INOTIFY_SUPPORT):
        self.menu = GtkMenu(self.destroy,self.ExecuteAction)
        self.notifier = notifier

        config = ConfigController()
        self.terminal = config.getValue('terminal')
        self.systray = config.getValue('systray')
        self.hideList = config.getValue('hide_list').split(',')
        self.showFavorites = config.getValue('favorites')

        self.makemenu = snapfly_core.MakeMenu(self.ExecuteAction,
                                self.move_on_scroll_event, self.terminal,
                                self.hideList, self.showFavorites)

        #self.menu.len = self.makemenu.make(self.menu.nbook)
        self.menu.set_menu(self.makemenu.get_menu())
        self.menu.create_menu(self.makemenu.get_favorites(),snapfly_core.cat_icon)

        self.INOTIFY_SUPPORT = INOTIFY_SUPPORT
        if self.systray == "true":
            self.tray = TrayIcon(self.menu.toggle_hide, self.doQuit)
            self.menu.set_tray_icon(self.tray)

    def doQuit(self, *gtk_args):
        gtk.main_quit()

    def run(self):
        gtk.main()

    def update_menu(self):
        if not self.updating:
            self.updating = True
            self.menu.set_menu(self.makemenu.get_menu())
            self.menu.create_menu(self.makemenu.get_favorites(),snapfly_core.cat_icon)
            self.updating = False

    def ExecuteAction(self, widget, event, cmd):
        self.focus_check = False
        launch_command(cmd)
        self.menu.toggle_hide(widget, event)

    def callback_signal(self):
        self.menu.mode = "mouse"
        self.menu.toggle_hide()
        self.menu.mode = None

    def callback_signal_show(self, category):
        self.menu.mode = "mouse"
        self.menu.set_current_page(category)
        self.menu.toggle_hide()
        self.menu.mode = None

    def destroy(self):
        if self.INOTIFY_SUPPORT:
            self.notifier.stop()

    def move_on_scroll_event(self,*gtk_args):
        """
        Method, that have to been called when mouse moves at right part of menu.
        """
        self.mouse_at_scroll = True