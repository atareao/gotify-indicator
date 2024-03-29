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

import sys
import gi

try:
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    gi.require_version('AppIndicator3', '0.1')
    gi.require_version('GdkPixbuf', '2.0')
    gi.require_version('Notify', '0.7')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import AppIndicator3
from gi.repository import GdkPixbuf
from gi.repository import Notify
import os
import json
import webbrowser
import dbus
from config import _
from preferences import Preferences
import config
from configurator import Configuration
from client import GotifyClient
from message_dialog import MessageDialog
from cache import Cache
from pydub import AudioSegment
from pydub.playback import play

# also defined in client.py
SOCKET_ACTIVE = 1
SOCKET_INACTIVE = 0
SOCKET_ERROR = -1

class Indicator(object):

    def __init__(self):

        self.indicator = AppIndicator3.Indicator.new(
            'gotify-indicator',
            'gotify-indicator',
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_menu(self.build_menu())
        self.indicator.set_label('', '')
        self.notification = Notify.Notification.new('', '', None)
        self.gotify_client = None
        self.load_preferences()

    def set_icon(self, active=SOCKET_ACTIVE):
        if active == SOCKET_ACTIVE:
            if self.theme_light:
                icon = config.ICON_ACTIVED_LIGHT
            else:
                icon = config.ICON_ACTIVED_DARK
            self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
        elif active == SOCKET_ERROR:
            if self.theme_light:
                icon = config.ICON_ERROR_LIGHT
            else:
                icon = config.ICON_ERROR_DARK
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ATTENTION)
        else:
            if self.theme_light:
                icon = config.ICON_PAUSED_LIGHT
            else:
                icon = config.ICON_PAUSED_DARK
            self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
        self.indicator.set_icon(icon)

    def load_preferences(self):
        configuration = Configuration()
        preferences = configuration.get('preferences')
        self.theme_light = preferences['theme-light']
        self.application_name = preferences['application_name']

        self.stop()
        self.start()

    def build_menu(self):
        menu = Gtk.Menu()
        self.menu_toggle_service = Gtk.MenuItem.new_with_label(
            _('Start service'))
        self.menu_toggle_service.connect('activate', self.toggle_service)
        menu.append(self.menu_toggle_service)

        menu.append(Gtk.SeparatorMenuItem())

        menu_send_message = Gtk.MenuItem.new_with_label(
            _('Send message'))
        menu_send_message.connect('activate', self.on_send_message)
        menu.append(menu_send_message)

        menu.append(Gtk.SeparatorMenuItem())

        menu_preferences = Gtk.MenuItem.new_with_label(_('Preferences'))
        menu_preferences.connect('activate', self.show_preferences)
        menu.append(menu_preferences)

        menus_help = Gtk.MenuItem.new_with_label(_('Help'))
        menus_help.set_submenu(self.get_help_menu())
        menu.append(menus_help)

        menu.append(Gtk.SeparatorMenuItem())

        menu_quit = Gtk.MenuItem. new_with_label(_('Quit'))
        menu_quit.connect('activate', self.quit)
        menu.append(menu_quit)
        menu.show_all()
        return menu

    def on_send_message(self, widget):
        widget.set_sensitive(False)
        messageDialog = MessageDialog()
        response = messageDialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            text = messageDialog.get_text()
            if text != '':
                self.gotify_client.send_message(text)
        messageDialog.destroy()
        widget.set_sensitive(True)

    def show_preferences(self, widget):
        widget.set_sensitive(False)
        preferences_dialog = Preferences()
        response = preferences_dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            preferences_dialog.save()
            configuration = Configuration()
            preferences = configuration.get('preferences')
            self.theme_light = preferences['theme-light']
            self.application_name = preferences['application_name']

            if self.gotify_client is not None and \
                    self.gotify_client.is_running():
                self.stop()
                self.start()
        preferences_dialog.destroy()
        widget.set_sensitive(True)

    def get_help_menu(self):
        help_menu = Gtk.Menu()

        homepage_item = Gtk.MenuItem.new_with_label(_('Homepage'))
        homepage_item.connect(
            'activate',
            lambda x: webbrowser.open(
                'http://www.atareao.es/apps/gotify-indicator/'))
        help_menu.append(homepage_item)

        help_item = Gtk.MenuItem.new_with_label(_('Get help online...'))
        help_item.connect(
            'activate',
            lambda x: webbrowser.open(
                'http://www.atareao.es/apps/gotify-indicator/'))
        help_menu.append(help_item)

        translate_item = Gtk.MenuItem.new_with_label(_(
            'Translate this application...'))
        translate_item.connect(
            'activate',
            lambda x: webbrowser.open(
                'http://www.atareao.es/apps/gotify-indicator/'))
        help_menu.append(translate_item)

        bug_item = Gtk.MenuItem.new_with_label(_('Report a bug...'))
        bug_item.connect(
            'activate',
            lambda x: webbrowser.open('https://github.com/atareao\
/gotify-indicator/issues'))
        help_menu.append(bug_item)

        help_menu.append(Gtk.SeparatorMenuItem())

        twitter_item = Gtk.MenuItem.new_with_label(_('Found me in Twitter'))
        twitter_item.connect(
            'activate',
            lambda x: webbrowser.open('https://twitter.com/atareao'))
        help_menu.append(twitter_item)
        #
        github_item = Gtk.MenuItem.new_with_label(_('Found me in GitHub'))
        github_item.connect(
            'activate',
            lambda x: webbrowser.open('https://github.com/atareao'))
        help_menu.append(github_item)

        mastodon_item = Gtk.MenuItem.new_with_label(_('Found me in Mastodon'))
        mastodon_item.connect(
            'activate',
            lambda x: webbrowser.open('https://mastodon.social/@atareao'))
        help_menu.append(mastodon_item)

        about_item = Gtk.MenuItem.new_with_label(_('About'))
        about_item.connect('activate', self.menu_about_response)

        help_menu.append(Gtk.SeparatorMenuItem())

        help_menu.append(about_item)
        return help_menu

    def menu_about_response(self, widget):
        widget.set_sensitive(False)
        ad = Gtk.AboutDialog()
        ad.set_name(config.APPNAME)
        ad.set_version(config.VERSION)
        ad.set_copyright('Copyrignt (c) 2020\nLorenzo Carbonell')
        ad.set_comments(_('Gotify Indicator'))
        ad.set_license('''
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.''')
        ad.set_website('')
        ad.set_website_label('http://www.atareao.es')
        ad.set_authors(['Lorenzo Carbonell Cerezo <a.k.a. atareao>'])
        ad.set_translator_credits('Lorenzo Carbonell Cerezo <a.k.a. atareao>')
        ad.set_documenters(['Lorenzo Carbonell Cerezo <a.k.a. atareao>'])
        ad.set_artists(['Freepik <https://www.flaticon.com/authors/freepik>'])
        ad.set_logo(GdkPixbuf.Pixbuf.new_from_file(config.ICON))
        ad.set_icon(GdkPixbuf.Pixbuf.new_from_file(config.ICON))
        ad.set_program_name(config.APPNAME)

        monitor = Gdk.Display.get_primary_monitor(Gdk.Display.get_default())
        scale = monitor.get_scale_factor()
        monitor_width = monitor.get_geometry().width / scale
        monitor_height = monitor.get_geometry().height / scale
        width = ad.get_preferred_width()[0]
        height = ad.get_preferred_height()[0]
        ad.move((monitor_width - width)/2, (monitor_height - height)/2)

        ad.run()
        ad.destroy()
        widget.set_sensitive(True)

    def toggle_service(self, widget):
        if self.gotify_client is None:
            self.start()
        else:
            self.stop()

    def stop(self):
        self.set_icon(SOCKET_INACTIVE)
        if self.gotify_client is not None:
            if self.gotify_client.is_running():
                self.gotify_client.stopWebsocket()
        self.gotify_client = None
        self.menu_toggle_service.set_label(_('Start service'))

    def on_message(self, message):
        message = json.loads(message)
        icon = os.path.join(config.CACHE_DIR, str(message['appid']))
        if message['title'] != self.application_name:
            self.notification.update(message['title'],
                                     message['message'],
                                     icon)
            self.notification.show()
            try:
                sound = self.getNotificationSound()
                if sound.strip():
                    play(AudioSegment.from_mp3(sound))
            except Exception as e:
                print("Exception while playing sound: "+str(e))

    def getNotificationSound(self):
        path = ""  # os.path.join(config.SOUNDDIR, 'default.mp3')
        configuration = Configuration()
        preferences = configuration.get('preferences')
        try:
            custom_path = preferences['notification_sound']
            if custom_path:
                path = custom_path
        except:
            print("No setting for notificationsound")

        return path

    def start(self):
        configuration = Configuration()
        preferences = configuration.get('preferences')

        https_protocol = preferences['https_protocol']
        base_url = preferences['base_url']
        application_name = preferences['application_name']
        application_token = preferences['application_token']
        client_token = preferences['client_token']

        if base_url and application_name and application_token \
                and client_token:
            self.gotify_client = GotifyClient(https_protocol,
                                              base_url,
                                              application_name,
                                              application_token,
                                              client_token,
                                              self.on_message,
                                              True)
            self.gotify_client.set_icon_callback(self.set_icon)
            self.gotify_client.start()
            self.menu_toggle_service.set_label(_('Stop service'))
            return True
        message = _('Please configure Gotify Indicator')
        icon = os.path.join(config.ICONDIR, 'gotify-indicator.svg')
        self.notification.update('Gofify-Indictator',
                                 message,
                                 icon)
        self.notification.show()

    def quit(self, menu_item):
        self.stop()
        Gtk.main_quit()
        # If Gtk throws an error or just a warning, main_quit() might not
        # actually close the app
        sys.exit(0)


def main():
    if dbus.SessionBus().request_name(
        'es.atareao.GotifyIndicator') !=\
            dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
        print("application already running")
        exit(0)

    try:
        Cache.instanciate()
    except Exception as e:
        print('Could not cache images!'+str(e))

    Notify.init('Gotify')
    Indicator()
    Gtk.main()

if __name__ == '__main__':
    main()
