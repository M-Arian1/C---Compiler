from collections import defaultdict
from enum import Enum

class Error(Enum):
    INVALID_NUM       = "Invalid Number"
    INVALID_INPUT     = "Invalid Input"
    UNCLOSED_COMMENT  = "Unclosed Comment"
    UNMATCHED_COMMENT = "Unmatched Comment"


class StateType(Enum):
    INTER = 0
    ACCEPT = 1
    ERROR = 2
    END = 3

class State:
    def __init__(self, type=(StateType.INTER,), push_back_needed=False, name=None):
        self.type = type
        self.push_back_needed = push_back_needed
        self.name = name  # New name attribute

    def is_terminal(self):
        return self.type[0] in (StateType.ACCEPT, StateType.ERROR)

    def is_push_back_needed(self):
        return self.push_back_needed  # Fixed typo here

    def get_state_type(self):
        return self.type[0]
    
    def get_name(self):
        return str(self.name)  # Getter for the name attribute


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
        self.include((chr(0), chr(255)))
        return self

    def is_in_alphabet(self, char):
        in_includes = self.__is_in_ranges(self.include_ranges, char)
        in_excludes = self.__is_in_ranges(self.exclude_ranges, char)
        return in_includes and not in_excludes


class Automaton:
    def __init__(self, start_state, default_panic_alph=Alphabet()):
        self.start_state = start_state
        self.default_panic_state = State((StateType.ERROR, Error.INVALID_INPUT),name= "panic_state")
        self.states = [start_state]
        self.transitions = defaultdict(list)  # will replace this in a second
        self.default_panic_alph = default_panic_alph

        self.add_transition_to_panic(start_state)

    def add_transition_to_panic(self, from_state):
        """Fallback transition to panic state for undefined input."""
        # Now: one default fallback for any char in default_panic_alph
        self.transitions[from_state].append((self.default_panic_state, self.default_panic_alph))

    def get_start_state(self):
        return self.start_state

    def add_state(self, state, add_transition_to_panic=True):
        self.states.append(state)
        if add_transition_to_panic:
            self.add_transition_to_panic(state)

    def add_transition(self, from_state, to_state, alphabet):
        """In DFA — for each input char, one possible destination."""
        self.transitions[from_state].append((to_state, alphabet))

    def next_state(self, current_state, char):
        """Move deterministically to the next state based on the input character."""
        for to_state, alphabet in self.transitions[current_state]:
            if alphabet.is_in_alphabet(char):
                return to_state
        # If no alphabet matches, panic state should always be defined
        return self.default_panic_state
