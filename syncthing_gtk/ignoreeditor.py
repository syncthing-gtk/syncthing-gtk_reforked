#!/usr/bin/env python3
"""
Syncthing-GTK - Ignore Pattern Editor
"""


import logging
import os

from gi.repository import Gtk

from syncthing_gtk.tools import _  # gettext function
from syncthing_gtk.uibuilder import UIBuilder

log = logging.getLogger("IgnoreEditor")


class IgnoreEditor(object):
    """Standard looking about dialog"""

    def __init__(self, app, rid, file_location):
        # Store stuff
        self.app = app
        self.rid = rid
        self.file_location = file_location
        # Load UI
        self.setup_widgets()

    def __getitem__(self, name):
        """Convince method that allows widgets to be accessed via self["widget"]"""
        return self.builder.get_object(name)

    def show(self, parent=None):
        if parent is not None:
            self["dialog"].set_transient_for(parent)
        self["dialog"].set_visible(True)

    def close(self, *a):
        self["dialog"].set_visible(False)
        self["dialog"].destroy()

    def setup_widgets(self):
        # Load ui file
        self.builder = UIBuilder(self)
        self.builder.add_from_file(os.path.join(self.app.uipath, "ignore-editor.ui"))
        self["dialog"].connect("response", self.on_dialog_response)
        self["lblLocation"].set_markup(
            '%s <a href="file://%s">%s</a>'
            % (
                _("File location:"),
                os.path.join(os.path.expanduser(self.file_location), ".stignore"),
                os.path.join(self.file_location, ".stignore"),
            )
        )

    def on_dialog_response(self, dialog, response_type):
        if response_type == Gtk.ResponseType.CLOSE or response_type == Gtk.ResponseType.CANCEL or response_type == Gtk.ResponseType.DELETE_EVENT:
            self.close()
        elif response_type == Gtk.ResponseType.APPLY:
            self.btSave_clicked_cb()

    def on_lblLocation_activate_link(self, *a):
        # Called when user clicks on file location link. Clicking there
        # should open .stignore file in default text editor, allowing
        # user to edit it there. Saving file from this dialog afterwards
        # would overwrite his changes, so dialog closes itself to
        # prevent that from happening
        self.close()

    def btSave_clicked_cb(self, *a):
        start_iter = self["tbPatterns"].get_start_iter()
        end_iter = self["tbPatterns"].get_end_iter()
        text = self["tbPatterns"].get_text(start_iter, end_iter, True)
        self["tvPatterns"].set_sensitive(False)
        self["btSave"].set_sensitive(False)
        # TODO: Expect error and create appropriate callback for it
        self.app.daemon.write_stignore(self.rid, text, self.close, self.close)

    def load(self):
        self.app.daemon.read_stignore(self.rid, self.cb_data_loaded, self.cb_data_failed)

    def cb_data_failed(self, *a):
        # This should be next to impossible, so simply closing dialog
        # should be enough of "solution"
        log.error("Failed to load .stignore data: %s", a)
        self.close()

    def cb_data_loaded(self, text):
        self["tbPatterns"].set_text(text)
        self["tvPatterns"].grab_focus()
        self["tvPatterns"].set_sensitive(True)
        self["btSave"].set_sensitive(True)
