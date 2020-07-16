from lib.school_data import SchoolDataSet
from utils.const import join_path
from utils.const import PROJECT_ROOT
from utils.logger import log

__all__ = ["SchoolSearchEngine", "search_schools", "console_input_search"]

SEARCH = None


class SchoolSearchEngine:
    """Search functions with caching for quick results."""

    def __init__(self, dataset):
        self._whole_terms = list()
        self._build_cache(dataset)

    def _build_cache(self, dataset: list) -> None:
        """
        Cache consists of a string for each entry that can be searched for specific keywords

        Args:
            dataset: The schools list used to build the cache.
        """
        for i in dataset:
            self._whole_terms.append(" ".join([
                i.name.lower(),
                i.city.city.lower(),
                i.city.state.lower()]))

    def _match_words(self, words: list, options: list = None) -> list:
        """
        Whole-word search, using recursion.

        Args:
            words: List of words to match with the options.
            options: Optional, list of phrases used in the search.

        Returns:
             List of matches.
        """
        # If this is the first level, use the whole terms list.
        options = options or self._whole_terms
        # Ensure there are words to use in the search.
        if len(words) == 0:
            return options
        # Perform matching on the first word.
        remaining_options = [option for option in options if words[0] in option]

        # Interpret results.
        if len(remaining_options) == 0:  # Nothing matches the first word in the set.
            if len(words) > 1:  # If there are additional words, skip the current word and search again.
                remaining_options = self._match_words(words[1:], options)
            else:
                return options[:3]
        if len(words) == 1:  # If current word is the last, return results.
            return remaining_options[:3]
        if len(remaining_options) <= 3:  # If remaining options are less than 3, return results
            return remaining_options
        # Only reaches here if the following conditions are true:
        # - More than one word left to search
        # - More than 3 values in `remaining_options`
        results = self._match_words(words[1:], remaining_options)
        # Sometimes results will return with less than 3 options, if so, we want to add
        # additional options that are considered the "next-best hit"
        while len(results) < 3:
            next_option = remaining_options.pop()
            if next_option not in results:
                results.append(remaining_options.pop())
        return results

    def phrase(self, phrase: str) -> list:
        """
        Perform a search for the phrase provided.

        Args:
            phrase: phrase to search for.

        Returns:
             List of 3 potential matches.
        """
        words = phrase.split(" ")
        try:
            return self._match_words(words)
        except Exception as e:
            log.error("Search error.")
            log.exception(e)
            return []


def search_schools(search_phrase: str, dataset=None):
    """
    Search the schools dataset for specific key-phrases

    Args:
        search_phrase: String used to search the database.
        dataset: Optional, only used to build the SchoolSearchEngine
          if it has not already been initialized.

    Returns:
        List of results from the schools dataset.
    """
    global SEARCH
    # First run, `SEARCH` will not be initialized.
    if SEARCH is None:
        if dataset is None:
            # Dataset may be provided, if already built. Otherwise, build it now.
            log.info("Setting up: Reading CSV, this may take a minute...")
            dataset = SchoolDataSet()
            dataset.load_csv(join_path(PROJECT_ROOT, "school_data.csv"))
        log.info("Setting up: Cache is being built.")
        SEARCH = SchoolSearchEngine(dataset.schools)
    # Perform search.
    log.debug(f"Searching for `{search_phrase}`")
    return SEARCH.phrase(search_phrase)


def console_input_search(dataset, force_update: bool = False) -> None:
    """
    Loop a console input, prompting for search terms until `q` is entered.

    Args:
        dataset: List containing `school_data.School` objects
        force_update: Forces the cache (`SchoolSearchEngine` object) to be rebuilt.

    Returns:
         None - All output is printed to stdout.
    """
    global SEARCH
    if SEARCH is None or force_update:  # Build the cache if it's not already present.
        print("Initializing search...")
        SEARCH = SchoolSearchEngine(dataset)
    print("Search started. Type `Q` or `q` to quit. Search is not case-sensitive. "
          "Incorrect spelling will not be adjusted.")
    # Loop so that multiple searches can be submitted in quick succession.
    while True:
        try:
            response = input("Enter search term: ").lower()
        except KeyboardInterrupt:
            log.info("Exiting...\n")
            break
        # Ignore empty input.
        if response == "":
            continue
        # Exit condition
        if response.lower() == "q":
            break
        # Perform and print search results.
        results = SEARCH.phrase(response)
        for i in range(len(results)):
            print(f"{i}: {results[i]}")
