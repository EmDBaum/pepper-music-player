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
"""View of the playlist."""

from importlib import resources

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from pepper_music_player.library import database
from pepper_music_player.metadata import entity
from pepper_music_player.metadata import token
from pepper_music_player.player import playlist
from pepper_music_player.ui import library_card


class ListItem(library_card.ListItem):
    """List item.

    Attributes:
        playlist_entry: Entry for the row.
    """

    def __init__(
            self,
            library_token: token.LibraryToken,
            playlist_entry: entity.PlaylistEntry,
    ) -> None:
        super().__init__(library_token)
        self.playlist_entry = playlist_entry
