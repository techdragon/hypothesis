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

from hypothesis.internal.conjecture.junkdrawer import LazySequenceCopy


class RemovableSampler(object):
    """A sampler from integer values in the range [0, n) which has the
    ability to remove values. All operations are amortized O(1)."""

    __slots__ = ("__values", "__removed")

    def __init__(self, values):
        self.__values = LazySequenceCopy(values)
        self.__removed = None

    @property
    def empty(self):
        """Returns True if and only if the sampler currently has no values left
        that it can sample."""
        if not self.__values:
            return True

        if self.__removed is None or len(self.__removed) < len(self.__values):
            return False

        while len(self.__values) > 0:
            if self.__values[-1] not in self.__removed:
                return False
            self.__removed.discard(self.__values.pop())
        assert len(self.__values) == 0
        return True

    def sample(self, random):
        """Return a uniform at random value from the remaining contents of
        the sampler."""
        while True:
            if len(self.__values) == 0:
                raise ValueError("Cannot sample from empty collection")
            i = random.randrange(0, len(self.__values))
            v = self.__values[i]
            if self.__removed is None or v not in self.__removed:
                return self.__values[i]
            self.__removed.discard(v)
            j = len(self.__values) - 1
            if i != j:
                self.__values[i], self.__values[j] = self.__values[j], self.__values[i]
            self.__values.pop()

    def remove(self, value):
        """Removes ```value``` from the collection. Makes no attempt to
        validate that it is currently already in the collection."""
        if self.__removed is None:
            self.__removed = set()
        self.__removed.add(value)
