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

import hypothesis.strategies as st
from hypothesis import assume, given
from hypothesis.internal.compat import hrange
from hypothesis.internal.conjecture.removablesampler import RemovableSampler


@st.composite
def fake_random(draw):
    data = draw(st.data())

    class FR(object):
        def randrange(self, u, v):
            return data.draw(st.integers(u, v - 1), label="randrange(%r, %r)" % (u, v))

    return FR()


@given(fake_random(), st.integers(1, 100))
def test_sampler_is_in_range_without_removal(random, n):
    sampler = RemovableSampler(hrange(n))
    i = sampler.sample(random)
    assert 0 <= i < n


@given(
    random=fake_random(),
    n=st.integers(1, 100),
    removed=st.sets(st.integers(0, 99)),
    repeats=st.integers(1, 10),
)
def test_sampler_does_not_include_removed(random, n, removed, repeats):
    assume(len(removed) < n)
    sampler = RemovableSampler(hrange(n))
    for r in removed:
        sampler.remove(r)
    for _ in range(repeats):
        i = sampler.sample(random)
        assert 0 <= i < n
        assert i not in removed


@given(st.data())
def test_sampler_is_empty_only_when_all_removed(data):
    n = data.draw(st.integers(1, 100))
    p = data.draw(st.permutations(range(n)))
    sampler = RemovableSampler(hrange(n))
    for r in p:
        assert not sampler.empty
        sampler.remove(r)
    assert sampler.empty
