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
"""Play orders."""

import abc
import enum
import functools
import logging
from typing import Any, Callable, Optional, TypeVar

from pepper_music_player.metadata import entity
from pepper_music_player.player import playlist

T = TypeVar('T')


class StopError(Exception):
    """Exception to stop playback due to an error."""


class ErrorPolicy(enum.Enum):
    """What an Order should do when there's an error.

    Attributes:
        RETURN_NONE: Return None, as if it were a normal stop condition.
        RAISE_STOP_ERROR: Raise StopError.
        DEFAULT: Default policy if none is specified, RETURN_NONE.
    """
    RETURN_NONE = enum.auto()
    RAISE_STOP_ERROR = enum.auto()
    DEFAULT = RETURN_NONE


def handle_stop_error(function: Callable[..., T]) -> Callable[..., Optional[T]]:
    """Decorator to handle ErrorPolicy for a function.

    Args:
        function: A function with an 'error_policy' keyword argument, that
            raises StopError on error.

    Returns:
        A function that respects the error_policy argument.
    """

    # TODO(https://github.com/google/pytype/issues/511): Remove pytype disable.
    # TODO(https://github.com/google/yapf/issues/793): Remove yapf disable.
    @functools.wraps(function)
    def _wrapper(
            *args: Any,
            error_policy: ErrorPolicy = ErrorPolicy.DEFAULT,
            **kwargs: Any,
    ) -> Optional[T]:  # pytype: disable=invalid-annotation  # yapf: disable
        try:
            return function(*args,
                            error_policy=ErrorPolicy.RAISE_STOP_ERROR,
                            **kwargs)
        except StopError:
            if error_policy is ErrorPolicy.RAISE_STOP_ERROR:
                raise
            else:
                assert error_policy is ErrorPolicy.RETURN_NONE
                logging.exception('Stopping due to error.')
                return None

    return _wrapper


class Order(abc.ABC):
    """Interface for play orders.

    Attributes:
        playlist: Playlist the order is following.
    """

    def __init__(self, playlist_: playlist.Playlist) -> None:
        """Initializer.

        Args:
            playlist_: Playlist.
        """
        self.playlist = playlist_

    # TODO(https://github.com/google/yapf/issues/793): Remove yapf disable.
    @abc.abstractmethod
    def next(
            self,
            current: Optional[entity.PlayableUnit],
            *,
            error_policy: ErrorPolicy = ErrorPolicy.DEFAULT,
    ) -> Optional[entity.PlayableUnit]:  # yapf: disable
        """Returns the next unit to play, or None if there's nothing next.

        Args:
            current: The currently playing unit, or None if nothing is playing.
            error_policy: What to do if there's an error.

        Raises:
            StopError: There's some error, so playback should stop. Note that
                this is raised only if error_policy is
                ErrorPolicy.RAISE_STOP_ERROR.
        """
        raise NotImplementedError()

    # TODO(https://github.com/google/yapf/issues/793): Remove yapf disable.
    @abc.abstractmethod
    def previous(
            self,
            current: Optional[entity.PlayableUnit],
            *,
            error_policy: ErrorPolicy = ErrorPolicy.DEFAULT,
    ) -> Optional[entity.PlayableUnit]:  # yapf: disable
        """Returns the previous unit, or None if there's no previous unit.

        This may also return None if the order just doesn't support going back
        to the previous unit, e.g., a random shuffle order that doesn't save its
        history.

        Args:
            current: The currently playing unit, or None if nothing is playing.
            error_policy: What to do if there's an error.

        Raises:
            StopError: There's some error, so playback should stop. Note that
                this is raised only if error_policy is
                ErrorPolicy.RAISE_STOP_ERROR.
        """
        raise NotImplementedError()


class LinearEntry(Order):
    """Plays a single entry through in order, then stops."""

    def _unit_in_same_entry(
            self,
            current: Optional[entity.PlayableUnit],
            *,
            offset: int,
    ) -> Optional[entity.PlayableUnit]:
        """Returns another playable unit within the same entry, or None.

        Args:
            current: The currently playing unit, or None if nothing is playing.
            offset: Offset from the current unit to the unit to return.

        Raises:
            StopError: Playback should stop because of an error.
        """
        if current is None:
            return None
        try:
            units = self.playlist.playable_units(current.playlist_entry)
        except KeyError:
            raise StopError('Current playlist entry not found.')
        try:
            index = {
                unit.track.token: index for index, unit in enumerate(units)
            }[current.track.token]
        except KeyError:
            raise StopError(
                f'Current track {current.track} does not exist in current '
                f'library entity {current.playlist_entry.library_token}.')
        # This uses an if-condition instead of `try ... except IndexError`
        # because index=0 and offset=-1 would return the last unit instead of
        # raising IndexError.
        if 0 <= index + offset < len(units):
            return units[index + offset]
        else:
            return None

    # TODO(https://github.com/google/yapf/issues/793): Remove yapf disable.
    @handle_stop_error
    def next(
            self,
            current: Optional[entity.PlayableUnit],
            *,
            error_policy: ErrorPolicy = ErrorPolicy.DEFAULT,
    ) -> Optional[entity.PlayableUnit]:  # yapf: disable
        """See base class."""
        del error_policy  # Unused.
        return self._unit_in_same_entry(current, offset=1)

    # TODO(https://github.com/google/yapf/issues/793): Remove yapf disable.
    @handle_stop_error
    def previous(
            self,
            current: Optional[entity.PlayableUnit],
            *,
            error_policy: ErrorPolicy = ErrorPolicy.DEFAULT,
    ) -> Optional[entity.PlayableUnit]:  # yapf: disable
        """See base class."""
        del error_policy  # Unused.
        return self._unit_in_same_entry(current, offset=-1)