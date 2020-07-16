import csv
import os
from enum import Enum
from typing import Union

from utils.typing import convert_type
from utils.logger import log


class SearchableEnum(Enum):
    """Add value searching with a try/except block to `Enum`"""

    @classmethod
    def find_val(cls, val):
        try:
            return cls(val)
        except ValueError:
            return None


class LocaleCodes(SearchableEnum):
    LARGE_CITY = 1
    MIDSIZE_CITY = 2
    URBAN_FRINGE_LARGE_CITY = 3
    URBAN_FRINGE_MIDSIZE_CITY = 4
    LARGE_TOWN = 5
    SMALL_TOWN = 6
    RURAL_OUTSIDE_CBSA = 7
    RURAL_INSIDE_CBSA = 8


class UrbanLocaleCodes(SearchableEnum):
    CITY_LARGE = 11
    CITY_MIDSIZE = 12
    CITY_SMALL = 13
    SUBURB_LARGE = 21
    SUBURB_MIDSIZE = 22
    SUBURB_SMALL = 23
    TOWN_FRINGE = 31
    TOWN_DISTANT = 32
    TIWN_REMOTE = 33
    RURAL_FRINGE = 41
    RURAL_DISTANT = 42
    RURAL_REMOTE = 43


class SchoolStatusCodes(SearchableEnum):
    OPERATIONAL = 1
    CLOSED = 2
    OPENED = 3
    OPERATIONAL_NEWLY_LISTED = 4
    NEW_AGENCY = 5
    TEMP_CLOSED = 6
    WILL_BE_OPERATIONAL = 7
    REOPENED = 8


class Search:
    """Search functionality to find existing class members with given values."""
    search_fields = dict()  # attr name & lambda function pair used in searching
    class_obj_list = list()  # class instances that get searched

    @classmethod
    def search(cls, **kwargs):
        """
        Search the current class for objects with the given set attributes.

        Args:
            kwargs: Key-value pairs used in the search. Note: additional values that
              are not in a class's `search_fields` will be ignored.
        """
        results = list()
        for obj in cls.class_obj_list:
            match = True
            for field in cls.search_fields:
                if field in kwargs and not cls.search_fields[field](obj, kwargs[field]):
                    match = False
            if match:
                results.append(obj)
        return results


class CountsMetadata:
    """Adds a basic metadata layer to a class."""
    _counts_lookup = dict()

    @classmethod
    def get_count_metadata(cls, name: str = None) -> Union[list, dict]:
        """
        Retrieves the metadata values specified by the provided args

        Args:
            name: metric name (key from `_counts_lookup`). If `name` is not provided,
              all values in `_counts_lookup` are returned.

        Returns:
            Dictionary is returned if name matches in `_counts_lookup`. If a name is not
            provided, a list of all metadata is returned.
        """
        if name is None:
            return [v for v in cls._counts_lookup.values()]
        if name in cls._counts_lookup:
            return cls._counts_lookup[name]
        log.warning(f"`{name}` was not found to be a valid code name in School metadata. "
                    f"Options are: {' '.join(cls._counts_lookup.keys())}")
        return []

    @staticmethod
    def increment_count_metadata(class_code: Enum, code_count_dict: dict) -> None:
        """
        Increment the designated metadata value.

        Args:
            class_code: Enum used for the name value used in `_counts_lookup`.
            code_count_dict: The dictionary where the enum name (`class_code`) is the key.
        """
        if class_code is None:
            return
        if class_code.name not in code_count_dict:
            code_count_dict[class_code.name] = 0
        code_count_dict[class_code.name] += 1


class City(Search, CountsMetadata):
    _counts_city = dict()
    _counts_state = dict()
    _counts_lookup = {
        "city": _counts_city,
        "state": _counts_state
    }

    class_obj_list = list()
    search_fields = {
        "city": lambda obj, val: obj.city == val,
        "state": lambda obj, val: obj.state == val
    }

    def __init__(self, city, state):
        self.city = city
        self.state = state
        self.class_obj_list.append(self)

    def __repr__(self):
        return f"{self.city}, {self.state}"

    def __str__(self):
        return self.__repr__()

    @property
    def number_of_cities(cls):
        return len(cls.class_obj_list)

    @classmethod
    def get_or_create(cls, city, state):
        """
        Get the class instance with the specified values, or create a new instance.

        Args:
            city: `City.city` value to search for.
            state: `City.state` value to search for.
        """
        # Ensure valid state format.
        if len(state) != 2:
            raise ValueError(f"State abbreviation must be 2 letters long. Found: {state}")
        # Perform search.
        match = cls.search(city=city, state=state)

        if city not in cls._counts_city:
            cls._counts_city[city] = 0
        cls._counts_city[city] += 1
        if state not in cls._counts_state:
            cls._counts_state[state] = 0
        cls._counts_state[state] += 1

        if len(match) == 0:
            return cls(city, state)
        # Otherwise, return the match. (there should only be one)
        # TODO: If there is an instance where search could return more than one
        #  result, add a condition to return all results.
        return match[0]


class Agency(Search):
    class_obj_list = list()
    search_fields = {
        "agency_id": lambda obj, val: obj.agency_id == val,
        "agency_name": lambda obj, val: obj.agency_name == val
    }

    def __init__(self, aid, name):
        self.agency_id = aid
        self.agency_name = name
        self.class_obj_list.append(self)

    def __repr__(self):
        return f"{self.agency_id}: {self.agency_name}"

    @classmethod
    def get_or_create(cls, agency_id, agency_name):
        """
        Get the class instance with the specified values, or create a new instance.

        Args:
            agency_id: `Agency.agency_id` value to search for.
            agency_name: `Agency.agency_name` value to search for.
        """
        # Search for matching Agency instance.
        match = cls.search(agency_id=agency_id, agency_name=agency_name)
        # If no matches are found, create a new class instance.
        if len(match) == 0:
            return cls(agency_id, agency_name)
        # Otherwise, return the match. (there should only be one)
        # TODO: (same as City class) If there is an instance where search could
        #  return more than one result, add a condition to return all results.
        return match[0]


class School(CountsMetadata):
    _locale_code_count = dict()
    _urban_code_count = dict()
    _status_code_count = dict()

    _counts_lookup = {
        "locale": _locale_code_count,
        "urban": _urban_code_count,
        "status": _status_code_count
    }

    def __init__(self, sid, agency_id, agency_name, name, city, state, lat, long, locale_code, urban_code, status_code):
        self.school_id = sid
        self.name = name
        self.agency = Agency.get_or_create(agency_id, agency_name)
        self.city = City.get_or_create(city, state)

        self.lat = convert_type(float, lat)
        self.long = convert_type(float, long)

        self.locale_code = LocaleCodes.find_val(convert_type(int, locale_code))
        self.increment_count_metadata(self.locale_code, self._locale_code_count)

        self.urban_code = UrbanLocaleCodes.find_val(convert_type(int, urban_code))
        self.increment_count_metadata(self.urban_code, self._urban_code_count)

        self.status_code = SchoolStatusCodes.find_val(convert_type(int, status_code))
        self.increment_count_metadata(self.status_code, self._status_code_count)

    def __str__(self):
        return f"{self.school_id}, {self.name} located in {self.city.city}, {self.city.state}"

    def __repr__(self):
        return f"{self.school_id}"


class SchoolDataSet:
    def __init__(self):
        self.schools = list()
        self._lookup_nces_id = {}

    def __len__(self):
        return len(self.schools)

    def _read_line(self, reader):
        # Get the next record to be evaluated.
        line = reader.__next__()
        # TODO: Some lines do not contain all values required. This could
        #  be revisited in the future to add completeness. Skipping lines
        #  that are incomplete for now.
        if len(line) != 11:
            return
        # Create a new school and add it to the class `schools` list.
        new_school = School(*line)
        self.schools.append(new_school)

    def load_csv(self, filepath, has_header=True):
        """Read a csv file and create `School` objects."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File at `{filepath}` was not found.")

        log.info(f"Processing {filepath}...")
        read_count = 0
        with open(filepath, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            if has_header:
                reader.__next__()
            while True:
                read_count += 1
                print(f"\rRead Count: {read_count}", end="")
                # Normally, I don't like to use a `while` loop that could get stuck in an infinite
                # loop, but for this particular instance, the `for` loop would not allow skipping
                # a single line if there was an issue in reading the file. I am instead leaving
                # the break up to the StopIteration exception
                try:
                    self._read_line(reader=reader)
                except UnicodeDecodeError:
                    # I was getting a UnicodeDecode error while reading the csv.
                    # As it currently stands, it will ignore the line where the
                    # error occurred and continue reading. This too could be revisited
                    # in the future.
                    log.warning("Line read error")
                    continue
                except ValueError as e:
                    log.warning("Invalid Value Found. " + str(e))
                    continue
                except StopIteration:
                    break
                except Exception as e:
                    log.warning("Unexpected exception: " + str(e))
                    log.exception(e)
                    continue
        print("\nNOTE: Read Count = Total lines read. It may not reflect "
              "how many records were created.\n-------")

    def _occurrence_count(self, fn) -> dict:
        """
        Internal method to get the occurrence using the function passed in.

        Args:
            fn: Function used to get the occurrence count of a target value
              from each school.

        Returns:
            A dictionary with the value as the key and the number
            of occurrences as the value.
        """
        results = dict()
        for school in self.schools:
            try:
                val = fn(school)
                if val not in results:
                    results[val] = 0
                results[val] += 1
            except:
                continue
        return results

    def state_occurrence_count(self):
        return self._occurrence_count(lambda x: x.city.state)

    def metro_occurrence_count(self):
        return self._occurrence_count(lambda x: x.locale_code.name)

    def city_occurrence_count(self):
        return self._occurrence_count(lambda x: x.city.city)


def find_max_schools_in_city(data) -> dict:
    """
    Find the most number of schools in a single city

    Args:
        data: Dictionary with city name as the key and number
          of occurrences in the value.

    Returns:
        Dictionary with only the city that has the highest count
          of schools and the count number in the following format:
          {"count": <int>, "city": <str>}
    """
    result = {
        "count": 0,
        "city": ""
    }
    # Iterate through each entry in the dict to find which
    # city has the highest number of schools.
    for k, v in data.items():
        if v > result["count"]:
            result["count"] = v
            result["city"] = k
    return result


def print_counts(dataset):
    """Print the information from the instructions in Part 1"""
    # Total number of schools:
    print(f"Total Schools: {len(dataset)}")

    # Schools by State:
    print("Schools by State:")
    for k, v in City.get_count_metadata("state").items():
        print(f"{k}: {v}")

    print("...")

    # Schools by Metro-centric Locale:
    print("Schools by Metro-centric Locale:")
    mcl = School.get_count_metadata("locale")
    for k, v in mcl.items():
        print(f"{k}: {v}")

    print("...")

    # City with the most schools:
    max_schools = find_max_schools_in_city(City.get_count_metadata("city"))
    print(f"City with the most schools: "
          f"{max_schools['city']} ({max_schools['count']} schools)")

    # Unique cities with at least one school:
    print(f"Unique cities with at least one school: {len(City.class_obj_list)}\n\n")
