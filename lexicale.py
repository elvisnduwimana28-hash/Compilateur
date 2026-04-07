import sys

class LexerL3:
    # Mots-clés de la grammaire L3
    KEYWORDS = {
        'program': 'PROGRAM_TOKEN', 'const': 'CONST_TOKEN', 'var': 'VAR_TOKEN',
        'begin': 'BEGIN_TOKEN', 'end': 'END_TOKEN', 'if': 'IF_TOKEN',
        'then': 'THEN_TOKEN', 'while': 'WHILE_TOKEN', 'do': 'DO_TOKEN',
        'write': 'WRITE_TOKEN', 'read': 'READ_TOKEN'
    }

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.TOKEN = None  # Type du token actuel
        self.SYM = ""      # Chaîne de caractères lue
        self.VAL = 0       # Valeur si c'est un NUM_TOKEN

    def NEXT_TOKEN(self):
        """Lit le caractère suivant et identifie le prochain token."""
        # Ignorer les espaces blancs
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

        if self.pos >= len(self.text):
            self.TOKEN = None
            self.SYM = "EOF"
            return

        char = self.text[self.pos]

        # 1. Identificateurs et Mots-clés
        if char.isalpha():
            start = self.pos
            while self.pos < len(self.text) and (self.text[self.pos].isalnum()):
                self.pos += 1
            self.SYM = self.text[start:self.pos]
            self.TOKEN = self.KEYWORDS.get(self.SYM.lower(), 'ID_TOKEN')
            return

        # 2. Nombres (Entiers)
        if char.isdigit():
            start = self.pos
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
            self.SYM = self.text[start:self.pos]
            self.VAL = int(self.SYM)
            self.TOKEN = 'NUM_TOKEN'
            return

        # 3. Symboles doubles (:=, <=, >=, <>)
        two_chars = self.text[self.pos:self.pos+2]
        operators_2 = {
            ':=': 'AFFEC_TOKEN', 
            '<=': 'INF_EGAL_TOKEN', 
            '>=': 'SUP_EGAL_TOKEN', 
            '<>': 'DIFF_TOKEN'
        }
        if two_chars in operators_2:
            self.SYM = two_chars
            self.TOKEN = operators_2[two_chars]
            self.pos += 2
            return

        # 4. Symboles simples
        operators_1 = {
            '+': 'PLUS_TOKEN', '-': 'MOINS_TOKEN', '*': 'MUL_TOKEN', '/': 'DIV_TOKEN',
            '=': 'EGAL_TOKEN', '<': 'INF_TOKEN', '>': 'SUP_TOKEN', '(': 'PAR_OUV_TOKEN',
            ')': 'PAR_FER_TOKEN', ',': 'VIRG_TOKEN', ';': 'PT_VIRG_TOKEN', '.': 'POINT_TOKEN'
        }
        if char in operators_1:
            self.SYM = char
            self.TOKEN = operators_1[char]
            self.pos += 1
            return

        # Caractère non reconnu
        self.TOKEN = 'TOKEN_INCONNU'
        self.SYM = char
        self.pos += 1

# --- SCRIPT DE TEST DU LEXER ---
if __name__ == "__main__":
    # Voici le code source de test inclus directement
    test_code = """
    program TestLexer;
    const TVA = 20 ;
    var prix, total;
    begin
        read(prix);
        total := prix + (prix * TVA / 100);
        write(total)
    end.
    """
    
    print("=== TEST DE L'ANALYSEUR LEXICAL ===")
    lexer = LexerL3(test_code)
    lexer.NEXT_TOKEN()
    
    while lexer.TOKEN is not None:
        val_str = f" | VAL: {lexer.VAL}" if lexer.TOKEN == 'NUM_TOKEN' else ""
        print(f"[{lexer.TOKEN:<15}] -> '{lexer.SYM}'{val_str}")
        lexer.NEXT_TOKEN()
    print("=== FIN DU TEST ===\n")