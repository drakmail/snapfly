#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import os
import sys
import glob
import subprocess

from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.build import build
from distutils.dep_util import newer
from distutils.log import info
from src.version import Application

PO_DIR = "po"
MO_DIR = os.path.join("build", "mo")


class BuildLocales(build):
    def run(self):
        build.run(self)

        for po in glob.glob(os.path.join(PO_DIR, "*.po")):
            lang = os.path.basename(po[:-3])
            mo = os.path.join(MO_DIR, lang, Application.name + ".mo")

            directory = os.path.dirname(mo)
            if not os.path.exists(directory):
                os.makedirs(directory)

            if newer(po, mo):
                info("compiling %s -> %s" % (po, mo))
                try:
                    rc = subprocess.call(["msgfmt", po, "-o", mo])
                    if rc:
                        raise Warning, "msgfmt returned %d" % rc
                except Exception, e:
                    print "Building gettext files failed."
                    print "%s: %s" % (type(e), str(e))
                    sys.exit(1)


class Install(install_data):
    def run(self):
        self.data_files.extend(self._find_mo_files())
        install_data.run(self)

    def _find_mo_files(self):
        data_files = []
        for mo in glob.glob(os.path.join(MO_DIR, "*",
                                         "%s.mo" % Application.name)):
            lang = os.path.basename(os.path.dirname(mo))
            print "LANG: " + lang
            dest = os.path.join("share", "locale", lang, "LC_MESSAGES")
            data_files.append((dest, [mo]))
        return data_files

setup(name=Application.name,
      version=Application.version,
      description="Simple PyGTK menu app",
      author=["Alexandr Shmakov", "Alexandr Maslov"],
      author_email=["uno.kms@gmail.com", "drakmail@gmail.com"],
      url=Application.website,
      license="GNU General Public License (GPL)",
      platforms=["Linux"],
      classifiers=["Environment :: X11 Applications :: GTK",
                   "Intended Audience :: End Users/Desktop",
                   "License :: OSI Approved :: GNU General Public License (GPL)",
                   "Operating System :: POSIX :: Linux",
                   "Programming Language :: Python :: 2.6",
                   "Topic :: Desktop Environment",
                   "Topic :: Utilities"],
      requires=["gtk", "dbus", "gobject", "cairo", "pyinotify", "pango"],
      packages=["snapfly"],
      package_dir={"snapfly": "src"},
      py_modules=["snapfly_core", "gui", "version", "config", "debug", "launcher", "menu", "xdg"],
      scripts=["snapfly", "snapfly-show"],
      cmdclass={'build': BuildLocales, 'install_data': Install},
      data_files=[
              ("share/icons/hicolor/16x16/apps", ["icons/hicolor/16x16/apps/snapfly.png"]),
              ("share/icons/hicolor/22x22/apps", ["icons/hicolor/22x22/apps/snapfly.png"]),
              ("share/icons/hicolor/24x24/apps", ["icons/hicolor/24x24/apps/snapfly.png"]),
              ("share/icons/hicolor/32x32/apps", ["icons/hicolor/32x32/apps/snapfly.png"]),
              ("share/icons/hicolor/36x36/apps", ["icons/hicolor/36x36/apps/snapfly.png"]),
              ("share/icons/hicolor/48x48/apps", ["icons/hicolor/48x48/apps/snapfly.png"]),
              ("share/icons/hicolor/64x64/apps", ["icons/hicolor/64x64/apps/snapfly.png"]),
              ("share/icons/hicolor/72x72/apps", ["icons/hicolor/72x72/apps/snapfly.png"]),
              ("share/icons/hicolor/96x96/apps", ["icons/hicolor/96x96/apps/snapfly.png"]),
              ("share/icons/hicolor/128x128/apps", ["icons/hicolor/128x128/apps/snapfly.png"]),
              ("share/icons/hicolor/192x192/apps", ["icons/hicolor/192x192/apps/snapfly.png"]),
              ("share/icons/hicolor/256x256/apps", ["icons/hicolor/256x256/apps/snapfly.png"]),
              ("share/icons/hicolor/scalable/apps", ["icons/hicolor/scalable/apps/snapfly.svg"]),
              ("share/man/ru/man1", ["man/ru/snapfly.1"])])
