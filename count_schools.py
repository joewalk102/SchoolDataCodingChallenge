#! /usr/bin/env python3
import os

from lib import school_data
from lib import school_search


def print_counts(dataset):
    """Part 1"""
    school_data.print_counts(dataset)


def search_loop(dataset):
    """Part 2"""
    school_search.console_input_search(dataset)


def main():
    school_data_set = school_data.SchoolDataSet()
    school_data_set.load_csv(
        os.path.join(os.path.dirname(__file__), "school_data.csv"))

    print_counts(school_data_set.schools)
    search_loop(school_data_set.schools)


if __name__ == '__main__':
    main()
