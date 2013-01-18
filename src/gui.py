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
import cairo
from gtk import gdk
from debug import logINFO, logTRACEBACK, printERROR
import os
import pango
import gettext

_ = gettext.gettext

try:
    from config import ConfigController
    import snapfly_core
    from version import Application
    from launcher import launch_command
except ImportError:
    sys.stderr.write("Can't import snapfly menu modules.\nExiting\n")
    import traceback
    traceback.print_exc(sys.stderr)
    sys.exit(1)

class Window(gtk.Window):
    def __init__(self, window_type=gtk.WINDOW_TOPLEVEL):
        gtk.Window.__init__(self, window_type)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.stick()
        self.set_app_paintable(True)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.ENTER_NOTIFY |
                        gtk.gdk.LEAVE_NOTIFY)
        self.set_border_width(0)


class PopupWindow(Window):
    def __init__(self, bg_color, border_color, border=6):
        Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_UTILITY)
        self.focus_check = False
        self.add_events(gtk.gdk.FOCUS_CHANGE_MASK)
        self.connect('expose-event', self.expose)
        self.connect('size-allocate', self.win_size_allocate)
        self.bg_surface = None

        self.check_screen()
        self.set_border_width(int(border / 2) + 1)

        self.border = border
        self.bg_color = bg_color
        self.border_color = border_color

        self.width = 0
        self.height = 0

    def check_screen(self):
        # To check if the display supports alpha channels, get the colormap
        screen = self.get_screen()
        colormap = screen.get_rgba_colormap()
        if colormap is None:
            colormap = screen.get_rgb_colormap()
        # Now we have a colormap appropriate for the screen, use it
        self.set_colormap(colormap)

    def win_size_allocate(self, widget, allocation):
        x, y, width, height = allocation

        if self.width == width and self.height == height:
            return

        self.bg_surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, width, height)

        if not self.is_composited() and self.border > 0:
            bitmap = gtk.gdk.Pixmap(None, width, height, 1)
            cr = bitmap.cairo_create()
            # Clear the bitmap to False
            cr.set_source_rgb(0, 0, 0)
            cr.set_operator(cairo.OPERATOR_DEST_OUT)
            cr.paint()
            # Draw our shape into the bitmap using cairo
            cr.set_operator(cairo.OPERATOR_OVER)
            self.draw_shape(cr, x + 1, y + 1, width - 2, height - 2)
            self.shape_combine_mask(bitmap, 0, 0)

        cr = cairo.Context(self.bg_surface)
        ## Full transparent
        cr.set_source_rgba(0, 0, 0, 0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        ## Draw next over 'transparent window'
        cr.set_operator(cairo.OPERATOR_OVER)
        self.draw_shape(cr, x + 1, y + 1, width - 2, height - 2)

        self.width, self.height = width, height

    def expose(self, widget, event):
        # On X11 this function returns whether a compositing
        # manager is running for the widget's screen
        if self.is_composited:
            cr = widget.window.cairo_create()
            ## Full transparent window
            cr.set_source_rgba(0, 0, 0, 0)
            cr.set_operator(cairo.OPERATOR_SOURCE)
            cr.paint()
            ## paint background
            cr.set_source_surface(self.bg_surface, 0, 0)
            cr.paint()

    def draw_shape(self, cr, x, y, width, height, flag=False):
        r, g, b = self.bg_color
        opacity = 0.92
        #~ opacity = self.bar.opacity

        cr.translate(x, y)

        lg = cairo.LinearGradient(0, y, 0, y + height)
        i = 0.0
        while i <= 0.3:
            lg.add_color_stop_rgba(1 - i,
                    r - (i * r),
                    g - (i * g),
                    b - (i * b),
                    opacity)
            i += 0.1
        i = 0.7
        while i <= 1.0:
            lg.add_color_stop_rgba(1 - i,
                                   r - (1 - i) * r,
                                   g - (1 - i) * g,
                                   b - (1 - i) * b,
                                   opacity)
            i += 0.1

        radius = min(self.border, width / 2, height / 2)

        cr.move_to(0, radius)
        cr.arc(radius, radius, radius, 3.14, 1.5 * 3.14)
        cr.line_to(width - radius, 0)
        cr.arc(width - radius, 0 + radius, radius, 1.5 * 3.14, 0.0)
        cr.line_to(width, height - radius)
        cr.arc(width - radius, height - radius, radius, 0.0, 0.5 * 3.14)
        cr.line_to(radius, height)
        cr.arc(radius, height - radius, radius, 0.5 * 3.14, 3.14)
        cr.close_path()
        cr.set_source(lg)
        cr.fill()

        cr.save()
        #~ cr.translate(x, y)

        cr.move_to(0, radius)
        cr.arc(radius, radius, radius, 3.14, 1.5 * 3.14)
        cr.line_to(width - radius, 0)
        cr.arc(width - radius, 0 + radius, radius, 1.5 * 3.14, 0.0)
        cr.line_to(width, height - radius)
        cr.arc(width - radius, height - radius, radius, 0.0, 0.5 * 3.14)
        cr.line_to(radius, height)
        cr.arc(radius, height - radius, radius, 0.5 * 3.14, 3.14)
        cr.close_path()

        r, g, b = self.border_color
        cr.set_source_rgba(r, g, b, opacity)
        cr.set_line_width(2)
        cr.stroke()
        cr.restore()

        return False

class AboutSnapFly:
    def __init__(self):
        about = gtk.AboutDialog()
        about.set_program_name(Application.name_full)
        about.set_version(Application.version)
        about.set_website(Application.website)
        about.set_authors(["Drakmail", "NomerUNO", "Pythonist", "Πλάτων"])
        about.set_comments(snapfly_core._("Lightweight, DE-independent PyGTK menu"))
        about.set_logo_icon_name(Application.name)
        about.run()
        about.destroy()

class TrayIcon:
    """
    The System Tray Icon for SnapFly.
    """
    def __init__(self,activate,quit):
        """
        Init The System Tray Icon.
        @param activate: callback for SnapFly hide/show function.
        @param quit: callback for SnapFly quit function.
        """
        self.statusIcon = gtk.StatusIcon()
        self.statusIcon.set_from_icon_name(Application.name)
        self.statusIcon.set_visible(True)
        self.statusIcon.set_tooltip(Application.name_full)
        self.statusIcon.connect('popup-menu', self.status_icon_popup)
        self.statusIcon.connect('activate', activate)
        # context menu create
        self.popupMenu = gtk.Menu()
        # Add Exit String
        exit_item = gtk.ImageMenuItem (gtk.STOCK_QUIT)
        exit_item.connect("activate", quit)
        # Add About String
        about_item = gtk.ImageMenuItem (gtk.STOCK_ABOUT)
        about_item.connect("activate", self.create_about)
        self.popupMenu.add(about_item)
        self.popupMenu.add(exit_item)
        self.popupMenu.show_all()

    def status_icon_popup(self,*gtk_args):
        """
        Show systray menu.
        """
        self.popupMenu.popup(None, None, None, 1, 0)

    def create_about(self,gtk_widget):
        """
        Creates About Dialog.
        """
        AboutSnapFly()

    def get_geometry(self):
        """
        Returns statusIcon position
        @return: The StatusIcon position.
        """
        return self.statusIcon.get_geometry()[1]

class GtkMenu:
    def __init__(self,destroy,execute):
        """
        @param destroy: callback for destroy function (at this moment (@221) stops inotify)
        @param ExecuteAction: callback for launch_command function
        """
        self.window = None
        self.len = None
        self.menu = None
        self.nbook = None
        self.hide_me = False
        self.updating = False
        self.focus_check = False
        self.mode = None
        self.ExecuteAction = execute
        config = ConfigController()
        self.rounded = int(config.getValue('rounded'))
        self.menu_width = int(config.getValue('menu_width'))
        self.bg_color = config.getValue('bg_color')
        self.border_color = config.getValue('border_color')
        self.showFavorites = True if config.getValue('favorites') == 'true'  else False
        self.terminal = config.getValue('terminal')
        self.mouse_at_scroll = False
        self.tab_width = None
        self.destroy = destroy
        self.tray = None
        if config.getValue('category_click') == 'false':
            self.category_click = False
        else:
            self.category_click = True
        self.create_window()
        self.toggle_hide()

    def set_menu(self,menu):
        """
        Sets menu (list of categories with items)
         @param menu: list of categories with items
        """
        self.menu = menu
        self.len  = len(menu)

    def set_tray_icon(self,trayIcon):
        """
        Sets tray icon (for get geometry size)
        @param trayIcon: TrayIcon object
        """
        self.tray = trayIcon

    def create_window(self):
        """
        Creates SnapFly menu window.
        """
        bg_color_rgb = snapfly_core.hex2rgb(self.bg_color)
        border_color_rgb = snapfly_core.hex2rgb(self.border_color)
        self.window = PopupWindow(bg_color_rgb, border_color_rgb, self.rounded)
        self.window.add_events(gtk.gdk.FOCUS_CHANGE_MASK)
        if not self.category_click:
            self.window.connect("motion_notify_event", self.motion_notify_event)
        self.window.connect("focus-out-event", self.lost_focus)
        self.window.connect("key-press-event", self.onkeypress)
        self.window.connect("destroy", self.destroy)
        self.window.set_size_request(self.menu_width,-1)

        self.nbook = gtk.Notebook()
        self.nbook.show()
        self.nbook.set_tab_pos(gtk.POS_LEFT)
        self.nbook.set_border_width(0)
        self.window.add(self.nbook)
        self.window.show_all()

    def motion_notify_event(self,gtk_widget,event):
        """
        Opens Tab at current mouse position.
        """
        if not self.mouse_at_scroll:
            if event.is_hint:
                y = event.window.get_pointer()[1]
            else:
                y = event.y
            self.nbook.set_current_page(int(y // ( self.nbook.get_allocation().height / self.len )))
        self.mouse_at_scroll = False

    def lost_focus(self, *gtk_args):
        """
        Hide menu, when focus lost.
        """
        if self.focus_check:
            self.toggle_hide()

    def toggle_hide(self, *gtk_args):
        """
        Show/hide menu.
        """
        if self.hide_me:
            self.hide_me = False
            self.show_menu(self.mode)
            self.window.show()
            self.window.present()
            self.focus_check = True
        else:
            self.hide_me = True
            self.focus_check = False
            self.window.hide()

    def show_menu(self, mode=None):
        """
        Show menu at tray icon or at mouse pointer.
        """
        screen_width, screen_height = gtk.gdk.screen_width(), gtk.gdk.screen_height()
        self.window.set_keep_above(True)
        if not mode:
            rect = self.tray.get_geometry()
            y = rect[1]+rect[3]
            if rect[0] + self.menu_width > screen_width:
                x = screen_width - self.menu_width
            else:
                if not self.tab_width:
                    x = max( 0, rect[0] - self.menu_width/2 )
                    self.window.move(x,y)
                    self.window.present()
                    try:
                        self.tab_width = self.menu_width - self.nbook.get_children(
                        )[0].get_window().get_children()[1].get_size()[1]
                    except:
                        pass
                    else:
                        x = max( 0, rect[0] - self.tab_width)
                        self.window.move(x,y)
                else:
                    x = max( 0, rect[0] - self.tab_width)
            if rect[1] < (screen_height // 2):
                y = rect[1] + rect[3]
                self.window.move(x, y)
            else:
                width, height = self.window.get_size()
                self.window.move(x, gtk.gdk.screen_height() - height)
            self.window.present()
        else:
            rootwin = self.window.get_screen().get_root_window()
            w_width , w_height = self.window.get_size()
            x, y, mods = rootwin.get_pointer()
            if x + self.menu_width > screen_width:
                x = screen_width - self.menu_width
            if y + w_height > screen_height:
                y = screen_height - w_height
            self.window.move(x, y)
            self.window.present()

    def onkeypress(self, gtk_widget, event):
        """
        Hide menu, when Escape key pressed.
        """
        if event.keyval == gtk.keysyms.Escape:
            self.toggle_hide()

    #TODO: Проверить работоспособность
    def set_current_page(self,category):
        """
        Sets active category.
        @param category: category needs to be opened.
        """
        self.nbook.set_current_page(category)

    def move_on_scroll_event(self,*gtk_args):
        """
        Method, that have to been called when mouse moves at right part of menu.
        """
        self.mouse_at_scroll = True

    def pixbuf_from_file(self,filename, width=None, height=None):
        pixbuf = None
        if filename is not None or filename == '':
            if os.path.isfile(filename):
                try:
                    if not width and not height:
                        pixbuf = gdk.pixbuf_new_from_file(filename)
                    else:
                        width, height = int(width), int(height)
                        pixbuf = gdk.pixbuf_new_from_file_at_size(filename, width, height)
                except:
                    logINFO("is an image ? => %s" % filename)
                    pixbuf = None
            else:
                logINFO("is a image ? => %s" % filename)
        return pixbuf

    def image_button(self, label, image, size, desc):
        bt = gtk.Button()
        bt.set_relief(gtk.RELIEF_NONE)
        bt.set_border_width(0)
        bt.set_focus_on_click(False)
        bt.set_property('can-focus', False)
        if not label:
            label = "Unknown"
        if image is None:
            bt_image = gtk.Image()
            bt_image.set_from_icon_name('image-x-generic', 24)
        elif type(image) == gtk.Image:
            bt_image = image
        elif type(image) == gdk.Pixbuf:
            bt_image = gtk.Image()
            bt_image.set_from_pixbuf(image)
        else:
            bt_image = gtk.Image()
            pixbuf = self.pixbuf_from_file(image, size, size)
            bt_image.set_from_pixbuf(pixbuf)

        bt_image.show()

        if desc is None:
            desc = ""
        desc = desc.replace("&", "&amp;")

        bt_label = gtk.Label()
        bt_label.set_use_markup(True)
        bt_label.set_markup("{0}\n<span color='#aaaaaa'>{1}</span>".
                            format(label, desc))
        bt_label.set_ellipsize(pango.ELLIPSIZE_END)
        bt_label.set_alignment(0, 0.5)
        align = gtk.Alignment(1, 0, 0.95, 0.5)
        align.show()
        align.add(bt_label)

        box = gtk.HBox()
        box.set_border_width(2)
        box.pack_start(bt_image, False, False)
        box.pack_start(align)
        box.show()
        bt.add(box)
        bt.show_all()
        return bt

    def create_menu(self, favorites,cat_icons):
        """
        Makes GUI menu part
        @param favorites: favorites category
        @param cat_icons: icons for categories
        """
        cats = self.menu.keys()
        cats.sort()

        tmpBook = gtk.Notebook()
        tmpBook.set_tab_pos(gtk.POS_LEFT)
        tmpBook.set_border_width(0)

        if self.showFavorites:
            cats.insert(0, 'Favorites')
            self.menu['Favorites'] = favorites
        for category in cats:
            bBox = gtk.VBox()
            bBox.show()
            bBox.set_spacing(1)
            bBox.set_border_width(1)

            tab_box = gtk.HBox(False, 4)
            tab_label = gtk.Label(_(category))
            tab_icon = gtk.Image()

            if cat_icons[category][0] == '/':
                pixbuf = gdk.pixbuf_new_from_file(cat_icons[category])
                pixbuf = pixbuf.scale_simple(24, 24, gdk.INTERP_BILINEAR)
                tab_icon.set_from_pixbuf(pixbuf)
            else:
                tab_icon.set_from_icon_name(cat_icons[category], 24)

            tab_box.pack_start(tab_icon, False)
            tab_box.pack_start(tab_label, False)

            # needed, otherwise even calling show_all on the notebook won't
            # make the hbox contents appear.
            tab_box.show_all()

            scrolled = gtk.ScrolledWindow()

            tmpBook.append_page(scrolled, tab_box)

            category_list = self.menu[category]
            for item in sorted(category_list, key=lambda category_list: category_list[2]):
                if item[1] and item[1][0] != '/':
                    icon = gtk.Image()
                    icon.set_from_icon_name(item[1], 24)
                    button = self.image_button(item[2], icon, 24, item[4])
                else:
                    button = self.image_button(item[2], item[1], 24, item[4])
                button.set_tooltip_text(item[4])
                button.connect("button-release-event", self.ExecuteAction,
                               item[0])
                bBox.pack_start(button, False, False)

            scrolled.show()
            scrolled.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
            scrolled.add_with_viewport(bBox)

            scrolled.connect("motion_notify_event", self.move_on_scroll_event)

        tmpBook.show()
        self.window.remove(self.nbook)
        self.window.add(tmpBook)
        self.nbook.destroy()
        self.nbook = tmpBook
