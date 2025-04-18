from collections import defaultdict

from src.Automata import *
from src.Tokens import *




class Table:
    def __init__(self):
        pass 
    def write_to_file(self, text, path):
        with open(path, "w") as file:
            file.write(text)


class SymbolTable(Table):
    def __init__(self, keywords_list=[]):
        super().__init__()
        self.all_symbols = []
        self.line_no = 1
        
        for keyword in keywords_list:
            k = {}
            k["name"] = keyword
            self.all_symbols.append(k)
        
    def get_symbol_by_name(self, symbol):
        for sym in self.all_symbols:
            if symbol["name"] == sym["name"]:
                return sym
        return None
        
    def add_symbol(self, symbol):
        if self.get_symbol_by_name(symbol) is None:
            self.all_symbols.append(symbol)
            self.line_no += 1
    
    def sym_to_text(self):
        text = ""
        for i, sym in enumerate(self.all_symbols):
            text += f"{i+1}.\t{sym['name']}\n"
        return text


class ErrorTable(Table):
    def __init__(self):
        super().__init__()
        self.lexical_records = []
    
    def add_record(self, token, final_state, line_no):
        while len(self.lexical_records) <= line_no:
            self.lexical_records.append([])

        self.lexical_records[line_no].append({
            "token": token.strip(),
            "error": final_state.type[1].value,
            "line": line_no
        })
        
    def generate_error_text(self):
        if not self.lexical_records:
            return "There is no lexical error."
            
        text = ""
        for line in self.lexical_records:
            for rec in line:
                text += str(rec["line"]) +".\t(" + rec["token"] + ",\t" + rec["error"] + ")\t"
            if not line:
                continue
            else:
                text += "\n"
        return text


class TokenTable(Table):
    def __init__(self):
        super().__init__()
        self.tokens = []
        
    def add_token(self, state=None, token=None, line_no=None, state_type=None):
        if state and state.type == Token.COMMENT or (state and state.type == Token.WHITESPACE):
            return
            
        while len(self.tokens) <= line_no:
            self.tokens.append([])
            
        token_type = None
        if state_type:
            token_type = state_type[1].value
        elif isinstance(state.type, tuple) and len(state.type) > 1:
            token_type = state.type[1].value
        else:
            token_type = ""
        
        if not token_type == "":
            token = token.strip()
            self.tokens[line_no].append("(" + token_type + ",\t" + token + ")")
    
    def generate_text(self):
        final_text = ""
        for i, token_line in enumerate(self.tokens):
            if not token_line:
                continue
                
            text = f"{i}.\t"
            for rec in token_line:
                text += str(rec) + "\t"
            text += "\n"
            final_text += text
        return final_text
