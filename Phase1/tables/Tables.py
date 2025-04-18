from collections import defaultdict
from Phase1.src.Automata import *
from Phase1.src.Tokens import *

class SymbolTable:
    
    def __init__(self, keywords_list = []):
        self.all_symbols = []
        self.line_no = 1
        
        for keyword in keywords_list:
            k ={}
            k["name"] = keyword
            self.all_symbols.append(k)
        
    def get_symbol_by_name(self, symbol):
        for sym in self.all_symbols:
            if symbol["name"] == sym["name"]:
                return sym
        return None
        
    def add_symbol(self, symbol):
        if(self.get_symbol_by_name(symbol["name"]) == None):
            self.all_symbols.append(symbol)
            self.line_no += 1
    
    
    def sym_to_text(self):
        text = ""
        for sym in self.all_symbols:
            text += sym["name"] +"\n"
            
class ErrorTable:
    
    def __init__(self):
        self.lexical_records = []
    
    def add_record(self, token, final_state):
        self.lexical_records.append({"token" : token.strip , "error" : final_state.type[1].value})
        
    def generate_error_text(self):
        text = ""
        for rec in self.lexical_records:
            
            text += "(" +rec["token"] + ",\t" + rec["error"] +")\n"
        return text
    
    
class TokenTable:
    def __init__(self):
        self.tokens = []
        
    def add_token(self, state, token, line_no):
        if state.type == Token.COMMENT or state.type == Token.WHITESPACE :
            return
        self.tokens[line_no].append("(" + token.strip +",\t" + state.type[1].value + ")")
    
    def generate_text(self):
        final_text = ""
        for token_line in self.tokens:
            text = ""
            for rec in token_line:
                text += str(rec) + "\t"
            text += "\n"
            final_text += text
        return final_text
            
                
            
        
    
    
        
        
        
    
    
    
    
        
        
        
    
    
        
        