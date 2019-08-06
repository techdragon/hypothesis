# coding=utf-8
#
# This file is part of Hypothesis, which may be found at
# https://github.com/HypothesisWorks/hypothesis/
#
# Most of this work is copyright (C) 2013-2019 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# CONTRIBUTING.rst for a full list of people who may hold copyright, and
# consult the git log if you need to determine who owns an individual
# contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.
#
# END HEADER

from __future__ import absolute_import, division, print_function


from hypothesis.errors import InvalidArgument
from hypothesis.internal import charmap
from hypothesis.internal.compat import binary_type, hunichr
from hypothesis.internal.conjecture.utils import integer_range
from hypothesis.internal.intervalsets import IntervalSet
from hypothesis.searchstrategy.strategies import MappedSearchStrategy, SearchStrategy


class OneCharStringStrategy(SearchStrategy):
    """A strategy which generates single character strings of text type."""

    def __init__(
        self,
        whitelist_categories=None,
        blacklist_categories=None,
        blacklist_characters=None,
        min_codepoint=None,
        max_codepoint=None,
        whitelist_characters=None,
        encoding=None,
    ):
        assert set(whitelist_categories or ()).issubset(charmap.categories())
        assert set(blacklist_categories or ()).issubset(charmap.categories())
        intervals = charmap.query(
            include_categories=whitelist_categories,
            exclude_categories=blacklist_categories,
            min_codepoint=min_codepoint,
            max_codepoint=max_codepoint,
            include_characters=whitelist_characters,
            exclude_characters=blacklist_characters,
            encoding=encoding,
        )
        if not intervals:
            arguments = [
                ("whitelist_categories", whitelist_categories),
                ("blacklist_categories", blacklist_categories),
                ("whitelist_characters", whitelist_characters),
                ("blacklist_characters", blacklist_characters),
                ("min_codepoint", min_codepoint),
                ("max_codepoint", max_codepoint),
            ]
            raise InvalidArgument(
                "No characters are allowed to be generated by this "
                "combination of arguments: "
                + ", ".join("%s=%r" % arg for arg in arguments if arg[1] is not None)
            )
        self.intervals = IntervalSet(intervals)
        self.zero_point = self.intervals.index_above(ord("0"))

    def do_draw(self, data):
        i = integer_range(data, 0, len(self.intervals) - 1, center=self.zero_point)
        return hunichr(self.intervals[i])


class StringStrategy(MappedSearchStrategy):
    """A strategy for text strings, defined in terms of a strategy for lists of
    single character text strings."""

    def __init__(self, list_of_one_char_strings_strategy):
        super(StringStrategy, self).__init__(strategy=list_of_one_char_strings_strategy)

    def __repr__(self):
        return "%r.map(u''.join)" % self.mapped_strategy

    def pack(self, ls):
        return u"".join(ls)


class BinaryStringStrategy(MappedSearchStrategy):
    """A strategy for strings of bytes, defined in terms of a strategy for
    lists of bytes."""

    def __repr__(self):
        return "%r.map(bytearray).map(%s)" % (
            self.mapped_strategy,
            binary_type.__name__,
        )

    def pack(self, x):
        assert isinstance(x, list), repr(x)
        ba = bytearray(x)
        return binary_type(ba)


class FixedSizeBytes(SearchStrategy):
    def __init__(self, size):
        self.size = size

    def do_draw(self, data):
        return binary_type(data.draw_bytes(self.size))
