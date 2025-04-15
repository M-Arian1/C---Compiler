from enum import Enum


class NodeType(Enum):
    INTERMEDIATE = 0    # Normal state
    ACCEPTING = 1       # Final state (token accepted)
    REJECT = 2          # Error state


class Condition:
    def __init__(self):
        self.allowed_ranges = []
        self.blocked_ranges = []

    def allow(self, start, end=None):
        if end is None:
            end = start
        self.allowed_ranges.append((start, end))
        return self

    def block(self, start, end=None):
        if end is None:
            end = start
        self.blocked_ranges.append((start, end))
        return self

    def is_satisfied_by(self, char):
        allowed = any(start <= char <= end for start, end in self.allowed_ranges) if self.allowed_ranges else True
        blocked = any(start <= char <= end for start, end in self.blocked_ranges)
        return allowed and not blocked


class StateNode:
    def __init__(self, node_type=NodeType.INTERMEDIATE, action=None, accept_any_char=False):
        self.node_type = node_type
        self.action = action
        self.accept_any_char = accept_any_char
        self.transitions = []

    def add_path(self, condition, target_node):
        self.transitions.append((condition, target_node))
        return self

    def accepts_any_character(self):
        return self.accept_any_char

    def next(self, char):
        for condition, target_node in self.transitions:
            if condition.is_satisfied_by(char):
                return target_node
        return self.action if self.action else None


class AcceptingNode(StateNode):
    def __init__(self, action, should_rewind=False):
        super().__init__(node_type=NodeType.ACCEPTING, action=action, accept_any_char=True)
        self.should_rewind = should_rewind

    def needs_rewind(self):
        return self.should_rewind