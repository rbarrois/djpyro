# -*- coding: utf-8 -*-
# This code is published under the two-clause BSD license.

import unittest

ANSWER_TO_LIFE_UNIVERSE_EVERYTHING = 42

class ExampleTestCase(unittest.TestCase):
    def test_answer(self):
        self.assertEqual(42, ANSWER_TO_LIFE_UNIVERSE_EVERYTHING)
