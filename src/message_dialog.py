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
from basedialog import BaseDialog


class LeftLabel(Gtk.Label):
    def __init__(self, label):
        Gtk.Label.__init__(self)
        self.set_label(label)
        self.set_xalign(0)


class MessageDialog(BaseDialog):
    def __init__(self):
        BaseDialog.__init__(self, _('Preferences'), None, ok_button=True,
                            cancel_button=True)

    def init_ui(self):
        BaseDialog.init_ui(self)
        self.grid.attach(LeftLabel(_('Message:')), 0, 0, 1, 1)
        frame = Gtk.Frame()
        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_border_width(3)
        self.message = Gtk.TextView.new()
        scroll.add(self.message)
        frame.add(scroll)
        frame.set_size_request(400, 200)
        self.grid.attach(frame, 0, 1, 2, 2)

    def get_text(self):
        buffer = self.message.get_buffer()
        return buffer.get_text(buffer.get_start_iter(),
                               buffer.get_end_iter(),
                               True)


if __name__ == '__main__':
    messageDialog = MessageDialog()
    response = messageDialog.run()
    if response == Gtk.ResponseType.ACCEPT:
        print(messageDialog.get_text())
