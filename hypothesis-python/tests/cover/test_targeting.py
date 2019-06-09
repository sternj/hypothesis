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

import pytest

from hypothesis import example, given, strategies as st, target
from hypothesis.errors import InvalidArgument
from hypothesis.internal.compat import string_types


@example(0.0, "this covers the branch where context.data is None")
@given(observation=st.floats(allow_nan=False, allow_infinity=False), label=st.text())
def test_allowed_inputs_to_target(observation, label):
    target(observation, label)


@given(
    observation=st.floats(min_value=1, allow_nan=False, allow_infinity=False),
    label=st.sampled_from(["a", "few", "labels"]),
)
def test_allowed_inputs_to_target_fewer_labels(observation, label):
    target(observation, label)


@given(st.floats(min_value=1, max_value=10))
def test_target_without_label(observation):
    target(observation)


@given(
    st.lists(
        st.tuples(
            st.floats(allow_nan=False, allow_infinity=False),
            st.sampled_from(["a", "few", "labels"]) | st.text(),
        ),
        min_size=1,
    )
)
def test_multiple_target_calls(args):
    for observation, label in args:
        target(observation, label)


def everything_except(type_):
    # Note: we would usually stick to fater traditional or parametrized
    # tests to check that invalid inputs are rejected, but for `target()`
    # we need to use `@given` (to validate arguments instead of context)
    # so we might as well apply this neat recipe.
    return (
        st.from_type(type)
        .flatmap(st.from_type)
        .filter(lambda x: not isinstance(x, type_))
    )


@example(float("nan"), "")
@example(float("inf"), "")
@example(float("-inf"), "")
@example("1", "Non-float observations are invalid")
@example(0.0, ["a list of strings is not a valid label"])
@given(observation=everything_except(float), label=everything_except(string_types))
def test_disallowed_inputs_to_target(observation, label):
    with pytest.raises(InvalidArgument):
        target(observation, label)
