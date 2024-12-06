
from string import ascii_letters
from position import *
from errors import *

#######################################
# TOKENS
#######################################

#######################################
# CONSTANTS
#######################################

BOOL_FALSE = '0'
BOOL_TRUE = '1'
LETTERS = ascii_letters
DIGITS = '0123456789'
LETTERS_DIGITS = LETTERS + DIGITS

#######################################
# TOKENS & KEYWORDS
#######################################

#Boolean values
TT_TRUE         =   'TRUE'
TT_FALSE        =   'FALSE'

#strings for file names
TT_STRING       =   'STRING'

#for variables
TT_IDENTIFIER   =   'IDENTIFIER'
TT_KEYWORD      =   'KEYWORD'

TT_EQ           =   'EQ'

#for equivalence, non-equivalence comparisons
TT_EE           =   'EE'
TT_NE           =   'NE'

#Boolean operations
TT_AND		    =   'AND'
TT_OR           =   'OR'
TT_NOT          =   'NOT'
TT_XOR          =   'XOR'

#parentheses for changing order of operations, declaring functions
TT_LPAREN       =   'LPAREN'
TT_RPAREN       =   'RPAREN'

#For function parameters and return value
TT_COMMA        =   'COMMA'
TT_ARROW        =   'ARROW'

#For multiline functionality
TT_NEWLINE		= 	'NEWLINE'

#For comments
TT_HASH         =   '#'

#Denotes end of file
TT_EOF          =   'EOF'

KEYWORDS = [
    'VAR',
    'IF',
    'ELIF',
    'THEN',
    'ELSE',
    'WHILE',
    'FUNC',
	'END',
    'RETURN',
    'CONTINUE',
    'BREAK'
]

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        
        if pos_end:
            self.pos_end = pos_end.copy()
    
    def matches(self, type_, value):
        return self.type == type_ and self.value == value
    
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

#######################################
# LEXER
#######################################

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        #self.advance()

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char == '#':
                self.skip_comment()
            elif self.current_char in ';\n':
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '0':
                tokens.append(Token(TT_FALSE, 0, pos_start=self.pos))
                self.advance()
            elif self.current_char == '1':
                tokens.append(Token(TT_TRUE, 1, pos_start=self.pos))
                self.advance()
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char == '"':
                tokens.append(self.make_string())
            elif self.current_char == '+':
                tokens.append(Token(TT_OR, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_AND, pos_start=self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(TT_XOR, pos_start=self.pos))
                self.advance()   
            elif self.current_char == '.':
                tokens.append(Token(TT_NOT, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '!':
                token, error = self.make_not_equals()
                if error: return [], error
                tokens.append(token)
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                self.advance()
                if self.current_char == '>':
                    tokens.append(Token(TT_ARROW, pos_start=self.pos))
                    self.advance()
                else:
                    return [], ExpectedCharError(pos_start, self.pos, "'>' (after '-')")
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TT_EOF, pos_start=self.pos)) #tells us end of file
        return tokens, None

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)

    def make_string(self):
        string = ''
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t'
            }

        while self.current_char != None and (self.current_char != '"' or escape_character):
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()
            escape_character = False
    
        self.advance()
        return Token(TT_STRING, string, pos_start, self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

    def make_equals(self):
        tok_type = TT_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_EE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
    
    def skip_comment(self):
        self.advance()

        while self.current_char != '\,':
            self.advance()
        
        self.advance()