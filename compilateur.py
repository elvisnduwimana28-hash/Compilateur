import sys
from lexicale import LexerL3 # Importation de ton travail précédent

class CompilateurL3:
    def __init__(self, source_code):
        self.lexer = LexerL3(source_code)
        self.TABLESYM = []
        self.PCODE = []  # Tableau d'instructions final [cite: 33]
        self.OFFSET = 0  # Pour l'allocation mémoire [cite: 86]

    # --- MÉTHODES DE GÉNÉRATION (MACH) ---
    def GENERER1(self, inst):
        """Génère une instruction sans argument [cite: 199]"""
        self.PCODE.append((inst, None))

    def GENERER2(self, inst, arg):
        """Génère une instruction avec un argument [cite: 199]"""
        self.PCODE.append((inst, arg))

    # --- GESTION SÉMANTIQUE ---
    def ENTRERSYM(self, nom, classe, valeur=None):
        """Ajoute un symbole et gère l'offset pour les variables [cite: 97, 98]"""
        if any(s['NOM'].lower() == nom.lower() for s in self.TABLESYM):
            print(f"Erreur : '{nom}' est déjà déclaré.")
            sys.exit(1)
        
        # Pour les variables, on utilise l'OFFSET actuel comme adresse 
        # Pour les constantes, on stocke directement la valeur 
        adresse = self.OFFSET if classe == "VARIABLE" else (valeur if valeur is not None else 0)
        
        self.TABLESYM.append({'NOM': nom, 'CLASSE': classe, 'ADRESSE': adresse})
        if classe == "VARIABLE":
            self.OFFSET += 1

    def CHERCHERSYM(self, nom):
        """Recherche un symbole pour récupérer son adresse [cite: 101]"""
        for s in self.TABLESYM:
            if s['NOM'].lower() == nom.lower():
                return s
        print(f"Erreur Sémantique : '{nom}' non déclaré.")
        sys.exit(1)

    # --- ANALYSE ET GÉNÉRATION (Étape 4) ---
    def TEST_TOKEN(self, attendu):
        if self.lexer.TOKEN == attendu:
            self.lexer.NEXT_TOKEN()
        else:
            print(f"Erreur : Attendu {attendu}, trouvé {self.lexer.TOKEN}")
            sys.exit(1)

    def COMPILER(self):
        """Point d'entrée du compilateur [cite: 116]"""
        self.lexer.NEXT_TOKEN()
        self.TEST_TOKEN('PROGRAM_TOKEN')
        if self.lexer.TOKEN == 'ID_TOKEN':
            self.ENTRERSYM(self.lexer.SYM, "PROGRAMME")
            self.lexer.NEXT_TOKEN()
        self.TEST_TOKEN('PT_VIRG_TOKEN')
        
        self.BLOCK()
        
        self.GENERER1('HLT') # Fin du programme [cite: 115]
        self.TEST_TOKEN('POINT_TOKEN')
        return self.PCODE

    def BLOCK(self):
        """Gère les déclarations et réserve l'espace mémoire [cite: 107, 112]"""
        self.OFFSET = 0
        while self.lexer.TOKEN in ['CONST_TOKEN', 'VAR_TOKEN']:
            if self.lexer.TOKEN == 'CONST_TOKEN':
                self.lexer.NEXT_TOKEN()
                self.CONST_DECL()
            elif self.lexer.TOKEN == 'VAR_TOKEN':
                self.lexer.NEXT_TOKEN()
                self.VAR_DECL()
        
        # On réserve OFFSET places dans la pile pour les variables [cite: 112]
        self.GENERER2('INT', self.OFFSET)
        self.CORPS()

    def CONST_DECL(self):
        while True:
            nom = self.lexer.SYM
            self.lexer.NEXT_TOKEN()
            self.TEST_TOKEN('EGAL_TOKEN')
            self.ENTRERSYM(nom, "CONSTANTE", self.lexer.VAL)
            self.lexer.NEXT_TOKEN()
            if self.lexer.TOKEN == 'PT_VIRG_TOKEN':
                self.lexer.NEXT_TOKEN()
                break
            elif self.lexer.TOKEN == 'VIRG_TOKEN': self.lexer.NEXT_TOKEN()

    def VAR_DECL(self):
        while True:
            self.ENTRERSYM(self.lexer.SYM, "VARIABLE")
            self.lexer.NEXT_TOKEN()
            if self.lexer.TOKEN == 'VIRG_TOKEN': self.lexer.NEXT_TOKEN()
            elif self.lexer.TOKEN == 'PT_VIRG_TOKEN':
                self.lexer.NEXT_TOKEN()
                break

    def CORPS(self):
        if self.lexer.TOKEN == 'BEGIN_TOKEN':
            self.lexer.NEXT_TOKEN()
            self.INSTRUCTION()
            while self.lexer.TOKEN == 'PT_VIRG_TOKEN':
                self.lexer.NEXT_TOKEN()
                self.INSTRUCTION()
            self.TEST_TOKEN('END_TOKEN')

    def INSTRUCTION(self):
        if self.lexer.TOKEN == 'ID_TOKEN': self.AFFEC()
        elif self.lexer.TOKEN == 'IF_TOKEN': self.SI()
        elif self.lexer.TOKEN == 'WHILE_TOKEN': self.TANTQUE()
        elif self.lexer.TOKEN == 'WRITE_TOKEN': self.ECRIRE()
        elif self.lexer.TOKEN == 'READ_TOKEN': self.LIRE()

    def AFFEC(self):
        """Génère LDA <adr> -> EXPR -> STO [cite: 156, 172]"""
        entree = self.CHERCHERSYM(self.lexer.SYM)
        self.GENERER2('LDA', entree['ADRESSE']) # Empile l'adresse [cite: 169]
        self.lexer.NEXT_TOKEN()
        self.TEST_TOKEN('AFFEC_TOKEN')
        self.EXPR()
        self.GENERER1('STO') # Stocke la valeur [cite: 172]

    def ECRIRE(self):
        """Génère EXPR -> PRN [cite: 175, 179]"""
        self.lexer.NEXT_TOKEN()
        self.TEST_TOKEN('PAR_OUV_TOKEN')
        self.EXPR()
        self.GENERER1('PRN')
        while self.lexer.TOKEN == 'VIRG_TOKEN':
            self.lexer.NEXT_TOKEN()
            self.EXPR()
            self.GENERER1('PRN')
        self.TEST_TOKEN('PAR_FER_TOKEN')

    def LIRE(self):
        """Génère LDA <adr> -> INN [cite: 193, 194]"""
        self.lexer.NEXT_TOKEN()
        self.TEST_TOKEN('PAR_OUV_TOKEN')
        while True:
            entree = self.CHERCHERSYM(self.lexer.SYM)
            self.GENERER2('LDA', entree['ADRESSE'])
            self.GENERER1('INN') # Lit et stocke à l'adresse au sommet [cite: 18]
            self.lexer.NEXT_TOKEN()
            if self.lexer.TOKEN == 'VIRG_TOKEN': self.lexer.NEXT_TOKEN()
            else: break
        self.TEST_TOKEN('PAR_FER_TOKEN')

    # --- BRANCHEMENTS (IF / WHILE)  ---
    def SI(self):
        self.lexer.NEXT_TOKEN()
        self.COND()
        adr_saut = len(self.PCODE)
        self.GENERER2('BZE', 0) # Saut si faux (0) [cite: 29]
        self.TEST_TOKEN('THEN_TOKEN')
        self.INSTRUCTION()
        self.PCODE[adr_saut] = ('BZE', len(self.PCODE)) # Mise à jour de l'adresse

    def TANTQUE(self):
        debut_boucle = len(self.PCODE)
        self.lexer.NEXT_TOKEN()
        self.COND()
        adr_saut = len(self.PCODE)
        self.GENERER2('BZE', 0)
        self.TEST_TOKEN('DO_TOKEN')
        self.INSTRUCTION()
        self.GENERER2('BRN', debut_boucle) # Retour au test [cite: 28]
        self.PCODE[adr_saut] = ('BZE', len(self.PCODE))

    # --- EXPRESSIONS ---
    def COND(self):
        self.EXPR()
        op = self.lexer.TOKEN
        self.lexer.NEXT_TOKEN()
        self.EXPR()
        mapping = {'EGAL_TOKEN': 'EQL', 'DIFF_TOKEN': 'NEQ', 'SUP_TOKEN': 'GTR', 
                   'INF_TOKEN': 'LSS', 'SUP_EGAL_TOKEN': 'GEQ', 'INF_EGAL_TOKEN': 'LEQ'}
        self.GENERER1(mapping.get(op, 'EQL'))

    def EXPR(self):
        self.TERM()
        while self.lexer.TOKEN in ['PLUS_TOKEN', 'MOINS_TOKEN']:
            op = self.lexer.TOKEN
            self.lexer.NEXT_TOKEN()
            self.TERM()
            self.GENERER1('ADD' if op == 'PLUS_TOKEN' else 'SUB') # [cite: 129]

    def TERM(self):
        self.FACT()
        while self.lexer.TOKEN in ['MUL_TOKEN', 'DIV_TOKEN']:
            op = self.lexer.TOKEN
            self.lexer.NEXT_TOKEN()
            self.FACT()
            self.GENERER1('MUL' if op == 'MUL_TOKEN' else 'DIV') # [cite: 145, 146]

    def FACT(self):
        if self.lexer.TOKEN == 'ID_TOKEN':
            entree = self.CHERCHERSYM(self.lexer.SYM)
            if entree['CLASSE'] == 'VARIABLE':
                self.GENERER2('LDA', entree['ADRESSE'])
                self.GENERER1('LDV') # Récupère la valeur à l'adresse [cite: 24]
            else: 
                self.GENERER2('LDI', entree['ADRESSE']) # Charge la valeur constante [cite: 21]
            self.lexer.NEXT_TOKEN()
        elif self.lexer.TOKEN == 'NUM_TOKEN':
            self.GENERER2('LDI', self.lexer.VAL)
            self.lexer.NEXT_TOKEN()
        elif self.lexer.TOKEN == 'PAR_OUV_TOKEN':
            self.lexer.NEXT_TOKEN()
            self.EXPR()
            self.TEST_TOKEN('PAR_FER_TOKEN')

# --- SCRIPT DE LANCEMENT ---
if __name__ == "__main__":
    from Interpreteur import PCodeInterpreter
    
    source = """
    program TestFichier;
    const TVA = 22;
    var prix, total;
    begin
        read(prix);
        total := prix + (prix * TVA / 100);
        write(total)
    end.
    """
    
    # 1. Compilation
    compilo = CompilateurL3(source)
    pcode_genere = compilo.COMPILER()
    
    # 2. Exécution par l'interpréteur
    print("Code généré avec succès. Lancement de la machine...")
    interp = PCodeInterpreter(pcode_genere)
    interp.run()