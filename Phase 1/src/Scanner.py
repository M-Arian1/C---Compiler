
from src.Automata import StateNode, FinalStateNode


class Scanner:
    def __init__(self, root, input_reader, alphabet):
        self.root = root
        self.input_reader = input_reader
        self.alphabet = alphabet
        
    def get_line_no(self):
        return self.input_reader.get_line_no()
    
    def can_generate_token(self):
        return self.input_reader.next_char_exists()
        

    def get_next_token(self):
        current_state = self.root
        lexeme = ""
        line_number = self.get_line_no()

        while True:
            # If we've reached an accepting (final) state
            if isinstance(current_state, FinalStateNode):
                if current_state.needs_rewind() and lexeme:
                    self.input_provider.push_back(lexeme[-1])
                    lexeme = lexeme[:-1]
                return current_state.action(line_number, lexeme)

            # If the state has no transitions and is not a StateNode, treat it as a direct action
            if not isinstance(current_state, StateNode):
                return current_state(line_number, lexeme)

            # If there are no more characters to read, exit the loop
            if not self.input_provider.has_next():
                break

            next_char = self.input_provider.get_next_char()
            lexeme += next_char

            # If the character doesn't belong to the valid language set and the state doesn't accept all characters
            if next_char not in self.language and not current_state.accepts_any_character():
                return current_state.action(line_number, lexeme)

            # Move to the next state based on the character
            current_state = current_state.next(next_char)