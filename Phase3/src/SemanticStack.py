class SemanticStack:
    def __init__(self):
        self.stack = []
        self.sp = 0  # Tracks the number of items

    def push(self, value):
        """Add a new value on top of the stack."""
        self.stack.append(value)
        self.sp += 1

    def pop(self, count=1):
        """
        Remove 'count' items from the top of the stack.
        Returns the last removed item.
        """
        popped = {}
        while count > 1:
            self.sp -= 1
            popped.append(self.stack.pop())
            count -= 1
        self.sp -= 1
        return popped

    def is_empty(self):
        """Check if the stack is empty."""
        return len(self.stack) == 0

    def top(self, offset=0):
        """
        Peek at the item 'offset' positions below the top.
        Offset 0 means the very top.
        """
        return self.stack[self.sp - offset - 1]
