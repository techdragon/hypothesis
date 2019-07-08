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

from collections import defaultdict

from hypothesis.internal.compat import hrange
from hypothesis.internal.conjecture.removablesampler import RemovableSampler


class _DeadSampler(object):
    empty = True


DeadSampler = _DeadSampler()


class ChoiceTree(object):
    def __init__(self):
        self.root = TreeNode()

    @property
    def exhausted(self):
        sampler = self.root.sampler
        return sampler is not None and sampler.empty

    def step(self, random, f):
        assert not self.exhausted
        chooser = Chooser(self, random)
        try:
            f(chooser)
        except DeadBranch:
            pass
        chooser.finish()


class TreeNode(object):
    def __init__(self):
        self.sampler = None
        self.children = defaultdict(TreeNode)


class DeadBranch(Exception):
    pass


class Chooser(object):
    def __init__(self, tree, random):
        self.__random = random
        self.__tree = tree
        self.__node_trail = [tree.root]
        self.__choices = []
        self.__finished = False

    def choose(self, values, condition=lambda x: True):
        assert not self.__finished
        node = self.__node_trail[-1]
        if node.sampler is None:
            node.sampler = RemovableSampler(hrange(len(values)))

        while not node.sampler.empty:
            i = node.sampler.sample(self.__random)
            v = values[i]
            if condition(v):
                self.__choices.append(i)
                self.__node_trail.append(node.children[i])
                return v
            else:
                node.sampler.remove(i)
        raise DeadBranch()

    def finish(self):
        self.__finished = True
        assert len(self.__node_trail) == len(self.__choices) + 1
        self.__node_trail[-1].sampler = DeadSampler
        while len(self.__node_trail) > 1 and self.__node_trail[-1].sampler.empty:
            self.__node_trail.pop()
            assert len(self.__node_trail) == len(self.__choices)
            i = self.__choices.pop()
            target = self.__node_trail[-1]
            target.sampler.remove(i)
            target.children.pop(i, None)
