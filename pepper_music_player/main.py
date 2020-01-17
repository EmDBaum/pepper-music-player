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
"""Main application."""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from pepper_music_player.ui import application


def main() -> None:
    application.install_css()
    application.window().show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
