import streamlit as st
import sys
import io
import builtins
from contextlib import redirect_stdout

# Importation de tes modules
from lexicale import LexerL3
from syntaxe import ParserL3
from compilateur import CompilateurL3
from Interpreteur import PCodeInterpreter

st.set_page_config(page_title="Compilateur L3", page_icon="⚙️", layout="wide")

st.title(" TP Réalisation d’un Compilateur fait par Zéïnab , Maha & Elvis")
st.markdown("Développé pour l'analyse lexicale, syntaxique, sémantique et la génération de P-Code.")

st.sidebar.header("Entrées de l'utilisateur")
default_code = """program Test;
const TVA = 20;
var prix, total;
begin
    read(prix);
    total := prix + (prix * TVA / 100);
    write(total)
end."""

code_source = st.text_area("Code Source (Langage L3)", value=default_code, height=250)

user_inputs_str = st.sidebar.text_area("Valeurs d'entrée :", value="150")


if st.button("Compiler et Exécuter", type="primary"):
    
    # On prépare les entrées simulées pour remplacer le input()
    input_values = user_inputs_str.strip().split('\n') if user_inputs_str else []
    input_iter = iter(input_values)
    
    # Fonction pour remplacer le input() standard
    def mock_input(prompt=""):
        try:
            return next(input_iter)
        except StopIteration:
            return "0" # Valeur par défaut si on manque d'entrées
            
    builtins.input = mock_input

    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Analyse Lexicale", 
        "Table des Symboles", 
        "Génération P-Code", 
        "Sortie du Compilateur et erreurs"
    ])

    # On redirige la sortie console (print) pour l'afficher dans Streamlit
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            # 1. ANALYSE LEXICALE
            lexer_test = LexerL3(code_source)
            lexer_test.NEXT_TOKEN()
            tokens = []
            while lexer_test.TOKEN is not None:
                tokens.append({"Token": lexer_test.TOKEN, "Lexème": lexer_test.SYM, "Valeur": lexer_test.VAL})
                lexer_test.NEXT_TOKEN()
            
            with tab1:
                st.subheader("Tokens générés")
                st.dataframe(tokens, use_container_width=True)

            # 2. ANALYSE SYNTAXIQUE ET SÉMANTIQUE
            lexer_parser = LexerL3(code_source)
            parser = ParserL3(lexer_parser)
            parser.PROGRAMME()
            
            with tab2:
                st.subheader("Table des Symboles")
                st.dataframe(parser.TABLESYM, use_container_width=True)

            # 3. COMPILATION (GÉNÉRATION P-CODE)
            compilo = CompilateurL3(code_source)
            pcode = compilo.COMPILER()
            
            with tab3:
                st.subheader("Instructions P-CODE")
                # Formatage du P-Code pour un bel affichage
                pcode_formatted = [{"Ligne": i, "Instruction": inst, "Argument": arg if arg is not None else ""} for i, (inst, arg) in enumerate(pcode)]
                st.dataframe(pcode_formatted, use_container_width=True)

            # 4. INTERPRÉTATION
            interp = PCodeInterpreter(pcode)
            interp.run()

        except SystemExit:
            st.error("L'exécution s'est arrêtée suite à une erreur (voir onglet Erreurs).")
        except Exception as e:
            st.error(f"Une erreur inattendue est survenue : {e}")

    
    console_output = f.getvalue()

    
            
    with tab4:
        st.subheader("Compilateur & Interpréteur - Sortie Console")
        st.text(console_output)