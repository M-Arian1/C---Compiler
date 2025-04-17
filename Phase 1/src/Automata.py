from collections import defaultdict
from enum import Enum

class Error(Enum):
    INVALID_NUM       = "Invalid Number"
    INVALID_INPUT     = "Invalid Input"
    UNCLOSED_COMMENT  = "Unclosed Comment"
    UNMATCHED_COMMENT = "Unmatched Comment"

class StateType(Enum):
    DEF = 0
    ACCEPT = 1
    ERROR = 2


class State:
    def __init__(self, type=(StateType.DEF,)):
        self.type = type

    def is_terminal(self):
        return self.type[0] in (StateType.ACCEPT, StateType.ERROR)


class Alphabet:
    def __init__(self):
        self.include_ranges = []
        self.exclude_ranges = []

    def __is_in_ranges(self, ranges, char):
        for start, end in ranges:
            if start <= char <= end:
                return True
        return False

    def __add_to_ranges(self, ranges, char_range):
        if len(char_range) == 1:
            char_range = (char_range[0], char_range[0])
        ranges.append(char_range)

    def include(self, char_range):
        self.__add_to_ranges(self.include_ranges, char_range)
        return self

    def exclude(self, char_range):
        self.__add_to_ranges(self.exclude_ranges, char_range)
        return self

    def include_all_chars(self):
        self.include((chr(0), chr(127)))
        return self

    def is_in_alphabet(self, char):
        in_includes = self.__is_in_ranges(self.include_ranges, char)
        in_excludes = self.__is_in_ranges(self.exclude_ranges, char)
        return in_includes and not in_excludes


class Automaton:
    def __init__(self, start_state):
        self.start_state = start_state
        self.states = [start_state]
        self.transitions = defaultdict(list)

    def get_start_state(self):
        return self.start_state

    def add_state(self, state):
        self.states.append(state)

    def add_transition(self, from_state, to_state, alphabet):
        self.transitions[from_state].append((to_state, alphabet))

    def next_states(self, from_states, char):
        to_states = []
        for from_state in from_states:
            for to_state, alphabet in self.transitions[from_state]:
                if alphabet.is_in_alphabet(char) and to_state not in to_states:
                    to_states.append(to_state)
        return to_states
