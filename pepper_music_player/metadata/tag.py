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
"""Music tags."""

import collections
import enum
import functools
import operator
import re
from typing import Iterable, Mapping, Optional, Tuple, Union

import frozendict


class TagName(enum.Enum):
    """Name of a known tag.

    Code that needs to access specific tags (e.g., getting the track number)
    should use this enum. Code that works with arbitrary tags (e.g., running a
    user-entered query with tags specified by the user) may use str tag names
    instead.
    """
    ALBUM = 'album'
    ALBUMARTIST = 'albumartist'
    MUSICBRAINZ_ALBUMID = 'musicbrainz_albumid'
    TRACKNUMBER = 'tracknumber'


ArbitraryTagName = Union[TagName, str]


def _tag_name_str(tag_name: ArbitraryTagName) -> str:
    """Returns the str form of a tag name."""
    if isinstance(tag_name, TagName):
        return tag_name.value
    else:
        return tag_name


class Tags(frozendict.frozendict, Mapping[ArbitraryTagName, Tuple[str]]):
    """Tags, e.g., from a file/track or album.

    Note that tags can have multiple values, potentially even multiple identical
    values. E.g., this is a valid set of tags: {'a': ('b', 'b')}
    """

    # Track number tags are typically either simple non-negative integers, or
    # they include the total number of tracks like '3/12'. This matches both
    # types.
    _TRACKNUMBER_REGEX = re.compile(
        r'(?P<tracknumber>\d+)(?:/(?P<totaltracks>\d+))?')

    def __init__(self, tags: Mapping[str, Iterable[str]]) -> None:
        """Initializer.

        Args:
            tags: Tags to represent, as a mapping from each tag name to all
                values for that tag.
        """
        super().__init__({name: tuple(values) for name, values in tags.items()})

    def __getitem__(self, key: ArbitraryTagName) -> Tuple[str]:
        return super().__getitem__(_tag_name_str(key))

    def __contains__(self, key: ArbitraryTagName) -> bool:
        return super().__contains__(_tag_name_str(key))

    def one_or_none(self, key: ArbitraryTagName) -> Optional[str]:
        """Returns a single value, or None if there isn't exactly one value."""
        values = self.get(key, ())
        if len(values) == 1:
            return values[0]
        else:
            return None

    def singular(
            self,
            key: ArbitraryTagName,
            *,
            default: str = '[unknown]',
            separator: str = '; ',
    ) -> str:
        """Returns a single value that represents all of the tag's values.

        Args:
            key: Which tag to look up.
            default: What to return if there are no values.
            separator: What to put between values if there is more than one
                value.
        """
        return separator.join(self.get(key, (default,)))

    @property
    def tracknumber(self) -> Optional[str]:
        """The human-readable track number, if there is one."""
        tracknumber = self.one_or_none(TagName.TRACKNUMBER)
        if tracknumber is None:
            return None
        match = self._TRACKNUMBER_REGEX.fullmatch(tracknumber)
        if match is None:
            return tracknumber
        else:
            return match.group('tracknumber')


def compose(components_tags: Iterable[Tags]) -> Tags:
    """Returns the tags for an entity composed of tagged sub-entities.

    E.g., this can get the tags for an album composed of tracks. In general, the
    composite entity's tags are the intersection of its element's tags.

    Args:
        components_tags: Tags for all the components.
    """
    if not components_tags:
        return Tags({})

    tag_pair_counters = []
    for component_tags in components_tags:
        tag_pairs = []
        for name, values in component_tags.items():
            tag_pairs.extend((name, value) for value in values)
        tag_pair_counters.append(collections.Counter(tag_pairs))
    common_tag_pair_counter = functools.reduce(operator.and_, tag_pair_counters)

    tags = collections.defaultdict(list)
    for name, value in common_tag_pair_counter.elements():
        tags[name].append(value)
    return Tags(tags)