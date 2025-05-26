class ParseNode:
    def __init__(self, name, token=None):
        self.name = name                  # Symbol or rule name
        self.token = token                # Optional token matched
        self.children = []                # Child parse nodes

    def add_child(self, child):
        if child:
            self.children.append(child)

    def __str__(self, level=0, is_last=True, prefix=""):
        result = ""
        
        if level == 0:
            # Root node - no prefix
            result += str(self.name)
            if self.token:
                result += self._format_token()
            result += "\n"
        else:
            # Build the current line with proper box-drawing characters
            if is_last:
                current_prefix = "└── "
                next_prefix = prefix + "    "
            else:
                current_prefix = "├── "
                next_prefix = prefix + "│   "
            
            result += prefix + current_prefix
            
            # For terminal nodes (tokens), show only the token format
            if self.token:
                result += self._format_token()
            else:
                result += str(self.name)
            
            result += "\n"
            
            # Update prefix for children
            prefix = next_prefix
        
        # Process children
        for i, child in enumerate(self.children):
            is_last_child = (i == len(self.children) - 1)
            result += child.__str__(level + 1, is_last_child, prefix)
            
        return result
    
    def _format_token(self):
        """Format token in the standard (TYPE, value) format"""
        if not self.token:
            return ""
            
        if hasattr(self.token, 'type') and hasattr(self.token, 'value'):
            # Token object with type and value attributes
            token_type = self.token.type[1].name if hasattr(self.token.type[1], 'name') else str(self.token.type[1])
            return f"({token_type}, {self.token.value})"
        elif hasattr(self.token, 'type'):
            # Token object with type but accessing differently
            try:
                token_type = self.token.type[1].value if hasattr(self.token.type[1], 'value') else str(self.token.type[1])
                token_value = getattr(self.token, 'value', str(self.token))
                return f"({token_type}, {token_value})"
            except:
                # Fallback to simple string representation
                return f"({str(self.token)}, {str(self.token)})"
        else:
            # Simple token - infer type from content
            token_str = str(self.token)
            if token_str in ["void", "int", "if", "else", "while", "break", "return"]:
                return f"(KEYWORD, {token_str}) "
            elif token_str in ["+", "-", "*", "(", ")", "[", "]", "{", "}", ";", ",", "<", "==", "="]:
                return f"(SYMBOL, {token_str}) "
            elif token_str.isdigit():
                return f"(NUM, {token_str}) "
            elif token_str.isalpha() or '_' in token_str:
                return f"(ID, {token_str}) "
            elif token_str == "$":
                return f"$"
            else:
                return f"({token_str}, {token_str})"