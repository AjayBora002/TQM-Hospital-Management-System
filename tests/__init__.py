"""
HMS Tests Package Initialization
Enables HMS_TEST_MODE so running the test suite never pollutes production TQM CSVs.
"""
import os

os.environ["HMS_TEST_MODE"] = "1"
