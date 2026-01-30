# -*- coding: utf-8 -*-
#
# PI Background IP
# Copyright (c) 2026, Planet Innovation Pty Ltd
# 436 Elgar Rd, Box Hill, 3128, VIC, Australia
# Phone: +61 3 9945 7510
#
# The copyright to the computer program(s) herein is the property of
# Planet Innovation, Australia.
# The program(s) may be used and/or copied only with the written permission
# of Planet Innovation or in accordance with the terms and conditions
# stipulated in the agreement/contract under which the program(s) have been
# supplied.

import unittest

from mock_machine import register_as_machine

# Inject the mocked machine interface
register_as_machine()

from micropython_ft24cxxa import Ft2408A  # noqa: E402


class TestFt2408A(unittest.TestCase):
    def test_import(self):
        """Test that Ft2408A can be imported."""
        self.assertIsNotNone(Ft2408A)


if __name__ == "__main__":
    unittest.main()
