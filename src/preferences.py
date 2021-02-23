#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of gotify-indicator
#
# Copyright (c) 2020 Lorenzo Carbonell Cerezo <a.k.a. atareao>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import gi
try:
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
except ValueError as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import Gdk
import os
import config
import shutil
from config import _
from configurator import Configuration
from basedialog import BaseDialog


class LeftLabel(Gtk.Label):
    def __init__(self, label):
        Gtk.Label.__init__(self)
        self.set_label(label)
        self.set_xalign(0)

# class ClassicSwitch(Gt)


class Preferences(BaseDialog):
    def __init__(self):
        BaseDialog.__init__(self, _('Preferences'), None, ok_button=True,
                            cancel_button=True)
        self.load()

    def init_ui(self):
        BaseDialog.init_ui(self)
        self.grid.attach(LeftLabel(_('HTTPS Protocol:')), 0, 0, 1, 1)
        self.https_protocol = Gtk.Switch.new()
        self.https_protocol.set_halign(Gtk.Align.START)
        self.grid.attach(self.https_protocol, 1, 0, 1, 1)
        self.grid.attach(LeftLabel(_('Base url (without protocol):')),
                         0, 1, 1, 1)
        self.base_url = Gtk.Entry.new()
        self.grid.attach(self.base_url, 1, 1, 1, 1)

        self.grid.attach(Gtk.Separator(), 0, 2, 2, 1)

        self.grid.attach(LeftLabel(_('Application name')), 0, 3, 1, 1)
        self.application_name = Gtk.Entry.new()
        self.grid.attach(self.application_name, 1, 3, 1, 1)
        self.grid.attach(LeftLabel(_('Application token:')), 0, 4, 1, 1)
        self.application_token = Gtk.Entry.new()
        self.grid.attach(self.application_token, 1, 4, 1, 1)

        self.grid.attach(Gtk.Separator(), 0, 5, 2, 1)

        self.grid.attach(LeftLabel(_('Client token:')), 0, 6, 1, 1)
        self.client_token = Gtk.Entry.new()
        self.grid.attach(self.client_token, 1, 6, 1, 1)

        self.grid.attach(Gtk.Separator(), 0, 7, 2, 1)

        self.grid.attach(LeftLabel(_('Theme light:')), 0, 8, 1, 1)
        self.theme_light = Gtk.Switch.new()
        self.theme_light.set_halign(Gtk.Align.START)
        self.grid.attach(self.theme_light, 1, 8, 1, 1)
        self.grid.attach(LeftLabel(_('Autostart:')), 0, 9, 1, 1)
        self.autostart = Gtk.Switch.new()
        self.autostart.set_halign(Gtk.Align.START)
        self.grid.attach(self.autostart, 1, 9, 1, 1)

        self.grid.attach(Gtk.Separator(), 0, 11, 2, 1)
        self.grid.attach(LeftLabel(_('Notification Sound:')), 0, 12, 1, 1)
        self.notification_sound = Gtk.Entry.new()
        self.notification_sound.set_editable(False)
        self.notification_sound.connect('button_press_event', self.pickSound)
        self.grid.attach(self.notification_sound, 1, 12, 1, 1)
        self.notification_reset = Gtk.Button.new_with_label("Reset")
        self.notification_reset.connect("clicked", self.resetSound)
        self.grid.attach(self.notification_reset, 1, 13, 1, 1)

    def load(self):
        configuration = Configuration()
        preferences = configuration.get('preferences')

        self.https_protocol.set_active(preferences['https_protocol'])
        self.base_url.set_text(preferences['base_url'])
        self.application_name.set_text(preferences['application_name'])
        self.application_token.set_text(preferences['application_token'])
        self.client_token.set_text(preferences['client_token'])
        self.notification_sound.set_text("")
        try:
            self.notification_sound.set_text(preferences['notification_sound'])
        except:
            print("No custom notification set!")

        self.theme_light.set_active(preferences['theme-light'])

        autostart_file = 'gotify-indicator-autostart.desktop'
        if os.path.exists(os.path.join(
                os.getenv('HOME'), '.config/autostart', autostart_file)):
            self.autostart.set_active(True)
        else:
            self.autostart.set_active(False)

    def save(self):
        configuration = Configuration()
        preferences = configuration.get('preferences')

        preferences['https_protocol'] = self.https_protocol.get_active()
        preferences['base_url'] = self.base_url.get_text()
        preferences['application_name'] = self.application_name.get_text()
        preferences['application_token'] = self.application_token.get_text()
        preferences['client_token'] = self.client_token.get_text()
        preferences['notification_sound'] = self.notification_sound.get_text()

        preferences['theme-light'] = self.theme_light.get_active()

        configuration.set('preferences', preferences)
        configuration.save()

        autostart_file = 'gotify-indicator-autostart.desktop'
        autostart_file = os.path.join(
            os.getenv('HOME'), '.config/autostart', autostart_file)
        if self.autostart.get_active():
            if not os.path.exists(os.path.dirname(autostart_file)):
                os.makedirs(os.path.dirname(autostart_file))
            shutil.copyfile(config.AUTOSTART, autostart_file)
        else:
            if os.path.exists(autostart_file):
                os.remove(autostart_file)

    def resetSound(self, widget):
        self.notification_sound.set_text("")

    def pickSound(self, widget, event):
        # https://python-gtk-3-tutorial.readthedocs.io/en/latest/dialogs.html#filechooserdialog
        dialog = Gtk.FileChooserDialog(
            title="Please choose a Notification Sound", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        filter_text = Gtk.FileFilter()
        filter_text.set_name("mp3 files")
        filter_text.add_mime_type("audio/mpeg")
        dialog.add_filter(filter_text)

        if dialog.run() == Gtk.ResponseType.OK:
            self.notification_sound.set_text(dialog.get_filename())
        dialog.destroy()


if __name__ == '__main__':
    preferences = Preferences()
    response = preferences.run()
    if response == Gtk.ResponseType.ACCEPT:
        preferences.save()
    preferences.destroy()
