# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Helpers for screenshot testing."""

import os
import pathlib

import gi
gi.require_version('GLib', '2.0')
from gi.repository import GLib
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def register_widget(
        module_name: str,
        screenshot_name: str,
        widget: Gtk.Widget,
) -> None:
    """Registers a Widget for screenshot testing.

    If the TEST_ARTIFACT_DIR environment variable is set, this will save the
    screenshot there for manual observation or external automated testing.

    Args:
        module_name: Module that the test widget comes from, i.e., __name__.
        screenshot_name: A unique name for the screenshot within the test
            module.
        widget: Widget to take a screenshot of.
    """
    window = Gtk.OffscreenWindow()
    window.add(widget)
    window.show_all()
    GLib.idle_add(Gtk.main_quit)
    Gtk.main()
    artifact_dir = os.getenv('TEST_ARTIFACT_DIR')
    if artifact_dir is None:
        return
    screenshot_dir = pathlib.Path(artifact_dir).joinpath('screenshots')
    screenshot_dir.mkdir(exist_ok=True)
    window.get_surface().write_to_png(
        screenshot_dir.joinpath(f'{module_name}.{screenshot_name}.png'))