#!/usr/bin/env python
import sys
import warnings

from crew import Day01

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """
    Day01().crew().kickoff()

run()