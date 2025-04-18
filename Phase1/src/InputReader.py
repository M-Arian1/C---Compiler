class InputReader:
    def __init__(self, filename = "input.txt", buffer_size = 100):
        self.filename = filename
        self.buffer_pointer = 0
        self.buffer_size = buffer_size
        self.buffer = ""
        self.line_no = 1
        self.input_file = open(filename, "r")
        self.__load_buffer()
        
    def __load_buffer(self):
        self.buffer = self.input_file.read(self.buffer_size)
        if len(self.buffer) < self.buffer_size:
            self.buffer += chr(26)
        self.buffer_pointer = 0
        
    def _refill_buffer(self):
        self.__load_buffer()
        
    def has_next(self):
        if self.buffer_pointer < len(self.buffer):
            return True
        elif len(self.buffer) < self.buffer_size:
            return False
        else:
            self._refill_buffer()
            return self.has_next()

    def get_line_no(self):
        return self.line_no
    
    def push_back(self, char):
        if char == '\n':
            self.line_no -= 1
        if self.buffer_pointer > 0:
            self.buffer_pointer -= 1
        else:
            self.buffer = char + self.buffer
            
    def get_next_char(self):
        if self.buffer_pointer >= len(self.buffer):
            self._refill_buffer()

        next_char = self.buffer[self.buffer_pointer]
        self.buffer_pointer += 1

        if next_char == '\n':
            self.line_no += 1

        return next_char

