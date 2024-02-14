from flask import Flask, request, jsonify, render_template
import re
import os
import google.generativeai as genai


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')
def valider_requete_sql(requete):
    # Vérifier si la requête commence par une des commandes SQL
    commandes_sql = ['insert', 'select', 'delete', 'update']
    if not any(re.match(r'^\b{}\b'.format(cmd), requete.lower()) for cmd in commandes_sql):
        return False, 'La requête doit commencer par INSERT, SELECT, DELETE ou UPDATE'

    # Vérifier si la requête contient l'expression FROM
    if not re.search(r'\bfrom\b', requete.lower()):
        return False, 'La requête doit contenir l\'expression FROM'

    # Vérifier si les mots-clés WHERE et JOIN sont correctement orthographiés
    if 'where' in requete.lower() and not re.search(r'\bwhere\b', requete.lower()):
        return False, 'La clause WHERE doit être correctement orthographiée'

    if 'join' in requete.lower() and not re.search(r'\bjoin\b', requete.lower()):
        return False, 'La clause JOIN doit être correctement orthographiée'

    # Si la requête passe toutes les conditions, elle est considérée comme valide
    return True, 'La requête est valide'


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
def analyze_sql_query(input_text):
    model = genai.GenerativeModel('gemini-pro')

    input_with_context = f"Can you analyze the following SQL query and tell me if it's valid or not : '{input_text}' ?"
    generated_content = model.generate_content(input_with_context)
    response = generated_content.text
    if  "invalid" in response or "is not valid" in response:
        return {"status": "error", "message": "La requete n'est pas valide "}
    elif "is valid" in response:
        return {"status": "success", "message": "La requete est  valide"}
    else:
        return {"status": "error", "message": "Unexpected model response"}


    
@app.route('/valider_requete_sql', methods=['POST'])
def valider_requete_sql_endpoint():
    data = request.get_json()
    if 'requete' not in data:
        return jsonify({'erreur': 'Veuillez fournir une requête SQL'}), 400
    
    requete = data['requete'].strip().lower()
    
    # Valider la requête SQL
    valide, message = valider_requete_sql(requete)
    
    # Analyser la requête SQL avec GemAI
    gemini_result = analyze_sql_query(requete)
    
    # Fusionner les résultats de validation et d'analyse
    response = {'valide': valide,'gemini_result': gemini_result}
    
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)
