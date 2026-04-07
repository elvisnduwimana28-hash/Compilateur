import sys
from lexicale import LexerL3

class ParserL3:
    def __init__(self, lexer):
        self.lexer = lexer
        self.TABLESYM = []
        self.OFFSET = 0

    def erreur(self, message):
        print(f"\n--- ERREUR ---")
        print(f"Message : {message}")
        print(f"Symbole actuel : '{self.lexer.SYM}' (Type: {self.lexer.TOKEN})")
        print(f"Position : {self.lexer.pos}")
        sys.exit(1)

    # --- TABLE DES SYMBOLES ---
    def ENTRERSYM(self, nom, classe, valeur=None):
        if any(s['NOM'].lower() == nom.lower() for s in self.TABLESYM):
            self.erreur(f"L'identificateur '{nom}' est déjà déclaré !")
        
        entree = {
            'NOM': nom,
            'CLASSE': classe,
            'ADRESSE': self.OFFSET if classe == "VARIABLE" else (valeur if valeur is not None else 0)
        }
        if classe == "VARIABLE": self.OFFSET += 1
        self.TABLESYM.append(entree)

    def AFFICHER_TABLE(self):
        print("\n" + "="*60)
        print(f"{'INDEX':<7} | {'NOM':<15} | {'CLASSE':<12} | {'ADR / VAL':<10}")
        print("-" * 60)
        for i, s in enumerate(self.TABLESYM):
            print(f"{i:<7} | {s['NOM']:<15} | {s['CLASSE']:<12} | {s['ADRESSE']:<10}")
        print("="*60 + "\n")

    # --- ANALYSE SYNTAXIQUE ET SÉMANTIQUE ---
    def TEST_TOKEN(self, attendu, msg_erreur):
        if self.lexer.TOKEN == attendu:
            self.lexer.NEXT_TOKEN()
        else:
            self.erreur(msg_erreur)

    def PROGRAMME(self):
        self.lexer.NEXT_TOKEN()
        self.TEST_TOKEN('PROGRAM_TOKEN', "Le programme doit commencer par 'program'.")
        
        if self.lexer.TOKEN == 'ID_TOKEN':
            self.ENTRERSYM(self.lexer.SYM, "PROGRAMME")
            self.lexer.NEXT_TOKEN()
        else: self.erreur("Nom du programme attendu.")
        
        self.TEST_TOKEN('PT_VIRG_TOKEN', "';' attendu après le nom du programme.")
        
        self.DECLARATIONS()
        
        if self.lexer.TOKEN == 'BEGIN_TOKEN':
            self.CORPS()
        else:
            self.erreur(f"Attendu 'begin' ou une déclaration, mais trouvé '{self.lexer.SYM}'")
            
        self.TEST_TOKEN('POINT_TOKEN', "'.' attendu à la fin du programme.")
        print("Félicitations : Analyse syntaxique et sémantique réussie !")

    def DECLARATIONS(self):
        while self.lexer.TOKEN in ['CONST_TOKEN', 'VAR_TOKEN']:
            if self.lexer.TOKEN == 'CONST_TOKEN':
                self.lexer.NEXT_TOKEN()
                self.CONST_DECL()
            elif self.lexer.TOKEN == 'VAR_TOKEN':
                self.lexer.NEXT_TOKEN()
                self.VAR_DECL()

    def CONST_DECL(self):
        while True:
            if self.lexer.TOKEN == 'ID_TOKEN':
                nom = self.lexer.SYM
                self.lexer.NEXT_TOKEN()
                self.TEST_TOKEN('EGAL_TOKEN', f"'=' attendu pour la constante {nom}.")
                if self.lexer.TOKEN == 'NUM_TOKEN':
                    self.ENTRERSYM(nom, "CONSTANTE", self.lexer.VAL)
                    self.lexer.NEXT_TOKEN()
                else: self.erreur("Valeur numérique attendue.")
                
                if self.lexer.TOKEN == 'PT_VIRG_TOKEN':
                    self.lexer.NEXT_TOKEN()
                    break
                elif self.lexer.TOKEN == 'VIRG_TOKEN':
                    self.lexer.NEXT_TOKEN()
                else: self.erreur("';' ou ',' attendu.")
            else: self.erreur("Identificateur attendu dans la section const.")

    def VAR_DECL(self):
        while True:
            if self.lexer.TOKEN == 'ID_TOKEN':
                self.ENTRERSYM(self.lexer.SYM, "VARIABLE")
                self.lexer.NEXT_TOKEN()
                if self.lexer.TOKEN == 'VIRG_TOKEN':
                    self.lexer.NEXT_TOKEN()
                elif self.lexer.TOKEN == 'PT_VIRG_TOKEN':
                    self.lexer.NEXT_TOKEN()
                    break
                else: self.erreur("';' ou ',' attendu.")
            else: self.erreur("Identificateur attendu dans la section var.")

    def CORPS(self):
        self.lexer.NEXT_TOKEN() # Sauter BEGIN
        # Pour cette étape, on saute juste les instructions jusqu'à END
        while self.lexer.TOKEN not in ['END_TOKEN', None]:
            self.lexer.NEXT_TOKEN()
        self.TEST_TOKEN('END_TOKEN', "'end' attendu.")

if __name__ == "__main__":
    source_correct = """
    program TestLexer;
    const TVA = 20;
    var prix, total, marche;
    begin
        read(prix);
        total := prix + (prix * TVA / 100);
        write(total)
    end.
    """

    print("--- Test du compilateur ---")
    lexer = LexerL3(source_correct) # Changez par source_erreur pour voir l'erreur
    parser = ParserL3(lexer)
    parser.PROGRAMME()
    parser.AFFICHER_TABLE()