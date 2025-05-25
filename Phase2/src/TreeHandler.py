class ParseNode:
    def __init__(self, name, token=None):
        self.name = name                  # Symbol or rule name
        self.token = token                # Optional token matched
        self.children = []                # Child parse nodes

    def add_child(self, child):
        if child:
            self.children.append(child)

    def __str__(self, level=0):
        indent = "  " * level
        prefix = "├── " if level > 0 else ""
        result = f"{indent}{prefix}{self.name}"
        if self.token:
            if hasattr(self.token, 'type'):
                result += f" ({self.token.type[1].value}, {self.token.value})"
            else:
                result += f" -> {self.token}"
        result += "\n"
        for i, child in enumerate(self.children):
            is_last = i == len(self.children) - 1
            child_prefix = "└── " if is_last else "├── "
            child_indent = "    " if is_last else "│   "
            child_str = child.__str__(level + 1)
            if level == 0:
                result += child_str
            else:
                lines = child_str.splitlines()
                for j, line in enumerate(lines):
                    if j == 0:
                        result += indent + child_prefix + line[len(indent):] + "\n"
                    else:
                        result += indent + child_indent + line[len(indent):] + "\n"
        return result
