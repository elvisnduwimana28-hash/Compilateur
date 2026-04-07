class PCodeInterpreter:
    def __init__(self, program):
        self.PCODE = program  # Liste contenant les instructions à exécuter
        self.MEM = [0] * 1000 # Tableau simulant la mémoire vive (RAM) et la Pile (Stack)
        self.PC = 0           # Program Counter : Index de l'instruction actuelle
        self.SP = -1          # Stack Pointer : Index du dernier élément ajouté à la pile
        self.PS = "EXECUTION" # État de la machine (s'arrête si différent de "EXECUTION")

    # --- Méthodes d'instructions (Le Jeu d'Instructions) ---

    def ADD(self, _):
        self.SP -= 1 # On descend le pointeur car on va fusionner 2 valeurs en 1
        # On additionne la valeur sous le sommet et le sommet, puis on stocke au nouveau sommet
        self.MEM[self.SP] = self.MEM[self.SP] + self.MEM[self.SP + 1]

    def SUB(self, _):
        self.SP -= 1 # On descend le pointeur
        # Soustraction : sous-sommet - sommet
        self.MEM[self.SP] = self.MEM[self.SP] - self.MEM[self.SP + 1]

    def MUL(self, _):
        self.SP -= 1
        self.MEM[self.SP] = self.MEM[self.SP] * self.MEM[self.SP + 1]

    def DIV(self, _):
        self.SP -= 1
        # Division entière (// en Python)
        self.MEM[self.SP] = self.MEM[self.SP] // self.MEM[self.SP + 1]

    def EQL(self, _):
        self.SP -= 1
        # Compare si les deux valeurs du haut sont égales (1 si vrai, 0 si faux)
        self.MEM[self.SP] = 1 if self.MEM[self.SP] == self.MEM[self.SP + 1] else 0

    def NEQ(self, _):
        self.SP -= 1 # Différent de
        self.MEM[self.SP] = 1 if self.MEM[self.SP] != self.MEM[self.SP + 1] else 0

    def GTR(self, _):
        self.SP -= 1 # Plus grand que (Greater Than)
        self.MEM[self.SP] = 1 if self.MEM[self.SP] > self.MEM[self.SP + 1] else 0

    def LSS(self, _):
        self.SP -= 1 # Plus petit que (Less Than)
        self.MEM[self.SP] = 1 if self.MEM[self.SP] < self.MEM[self.SP + 1] else 0

    def GEQ(self, _):
        self.SP -= 1 # Supérieur ou égal
        self.MEM[self.SP] = 1 if self.MEM[self.SP] >= self.MEM[self.SP + 1] else 0

    def LEQ(self, _):
        self.SP -= 1 # Inférieur ou égal
        self.MEM[self.SP] = 1 if self.MEM[self.SP] <= self.MEM[self.SP + 1] else 0

    def LDI(self, v):
        self.SP += 1          # On fait de la place sur la pile
        self.MEM[self.SP] = v # On y dépose la valeur immédiate v

    def LDA(self, a):
        self.SP += 1          # On fait de la place
        self.MEM[self.SP] = a # On dépose l'adresse a sur la pile

    def LDV(self, _):
        # On lit l'adresse qui est au sommet de la pile
        addr = self.MEM[self.SP]
        # On remplace cette adresse par la valeur réelle trouvée à cette adresse (déréférencement)
        self.MEM[self.SP] = self.MEM[addr]

    def STO(self, _):
        val = self.MEM[self.SP]       # On récupère la valeur au sommet
        addr = self.MEM[self.SP - 1]  # On récupère l'adresse juste en dessous
        self.MEM[addr] = val          # On stocke la valeur dans la mémoire à l'adresse indiquée
        self.SP -= 2                  # On retire l'adresse et la valeur de la pile (dépile 2 fois)

    def BRN(self, a):
        self.PC = a # Saut inconditionnel : on force le PC à aller à l'index a

    def BZE(self, a):
        # Si la valeur au sommet est égale à 0 (faux)
        if self.MEM[self.SP] == 0:
            self.PC = a # On saute à l'instruction à l'index a
        self.SP -= 1    # Dans tous les cas, on dépile la valeur testée

    def INT(self, c):
        self.SP += c # Réserve 'c' places sur la pile (utilisé pour déclarer des variables)

    def HLT(self, _):
        self.PS = "FINI" # Change le statut pour arrêter la boucle while

    def PRN(self, _):
        print(f"> Sortie du programme: {self.MEM[self.SP]}") # Affiche le résultat en haut de pile
        self.SP -= 1                            # Dépile après affichage

    def INN(self, _):
        val = int(input("< Entrez un entier : ")) # Demande une saisie utilisateur
        addr = self.MEM[self.SP]                 # Lit l'adresse au sommet
        self.MEM[addr] = val                     # Stocke la saisie à cette adresse
        self.SP -= 1                             # Dépile l'adresse

    # --- Boucle de fonctionnement de la CPU ---

    def run(self):
        print("Début de l'interprétation...")
        # Tant que l'état est EXECUTION et qu'il reste des instructions
        while self.PS == "EXECUTION" and self.PC < len(self.PCODE):
            # 1. FETCH (Chargement) : On récupère l'instruction et son argument
            inst, arg = self.PCODE[self.PC]
            self.PC += 1 # On pointe déjà vers la prochaine instruction
            
            # 2. EXECUTE : On cherche si la méthode existe dans cette classe
            if hasattr(self, inst):
                methode = getattr(self, inst) # On récupère la fonction par son nom
                methode(arg)                  # On l'appelle avec son argument
            else:
                print(f"Erreur : Instruction {inst} inconnue.")
                break
        print("Fin de l'exécution.")

# --- Test du programme ---
# Ce code charge 5, puis 8, vérifie si 5 > 8 (Faux = 0), affiche 0, puis s'arrête.
programme2 = [
    ("LDI", 5),
    ("LDI", 8),
    ("MUL", None),
    ("PRN", None),
    ("HLT", None)
]
programme = [
    ("LDI", 5),
    ("LDI", 8),
    ("ADD", None),
    ("PRN", None),
    ("HLT", None)
]


"""interp = PCodeInterpreter(programme)
interp.run()
interp = PCodeInterpreter(programme2)
interp.run()"""

programme_addition = [
    ("LDA", 1),    # On prépare l'adresse mémoire 0
    ("INN", None), # L'utilisateur tape le 1er nombre (ex: 9) -> MEM[0] = 9
    
    ("LDA", 2),    # On prépare l'adresse mémoire 1
    ("INN", None), # L'utilisateur tape le 2ème nombre (ex: 9) -> MEM[1] = 9
    
    ("LDA", 1),    # On pointe vers l'adresse 0
    ("LDV", None), # On récupère la valeur (9) et on la met sur la pile
    
    ("LDA", 2),    # On pointe vers l'adresse 1
    ("LDV", None), # On récupère la valeur (9) et on la met sur la pile
    
    ("ADD", None), # On fait 9 + 9
    ("PRN", None), # On affiche le résultat (devrait afficher 18)
    ("HLT", None)  # Fin
]

"""interp = PCodeInterpreter(programme_addition)
interp.run()"""