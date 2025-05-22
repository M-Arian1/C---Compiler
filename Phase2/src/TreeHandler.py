
#TODO: Modify and complete it



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
        result = f"{indent}{self.name}"
        if self.token:
            result += f" -> {self.token.value}"
        result += "\n"
        for child in self.children:
            result += child.__str__(level + 1)
        return result
