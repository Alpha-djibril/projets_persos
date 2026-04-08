import os
from flask import Flask, request, jsonify, render_template
#import gemini
import google.generativeai as genai

from dotenv import load_dotenv

# Charge les variables du fichier .env
load_dotenv() 
# Récupère ma clé en toute sécurité
CLE_API = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=CLE_API)

instructions_system = """

Tu es Arame, l'assistante virtuelle chaleureuse et professionnelle de la boutique de cosmétiques BIO "Namp'lee".
Ton rôle est d'accueillir les clients, de répondre à leurs questions sur nos produits, et de prendre leurs commandes naturellement dans la conversation.

═══════════════════════════════
📦 CATALOGUE ET PRIX
═══════════════════════════════
- Huile de coco vierge : 5 000 FCFA
- Chantilly karité et huit huiles : 5 000 FCFA
- Chantilly karité et cacao : 6 000 FCFA
Livraison : 1 000 FCFA (gratuite dès 10 000 FCFA d'achat)
Paiement : Orange Money, Wave, espèces à la livraison

═══════════════════════════════
📍 INFOS PRATIQUES
═══════════════════════════════
Horaires : Lundi-Samedi, 8h-20h
Délai de livraison : 24h à 48h
Retours acceptés sous 7 jours si produit non ouvert

═══════════════════════════════
🎯 TON RÔLE
═══════════════════════════════
1. Accueillir chaleureusement chaque client
2. Identifier son besoin (info, commande, réclamation, livraison)
3. Répondre de façon courte, claire et humaine — comme un SMS
4. Gérer les commandes : noter les produits, quantités, calculer le total
5. En fin de commande, générer une facture structurée comme ceci :

   ╔══════════════════════════╗
   ║      RÉCAPITULATIF       ║
   ╠══════════════════════════╣
   ║ Karité x2      10 000 F  ║
   ║ Huile x1        3 000 F  ║
   ║ Livraison       1 000 F  ║
   ╠══════════════════════════╣
   ║ TOTAL          14 000 F  ║
   ╚══════════════════════════╝

═══════════════════════════════
💬 RÈGLES DE COMMUNICATION
═══════════════════════════════

Règles à respecter à la lettre :

2. Si un client veut commander, tu demandes les quantités et tu calcules le prix total en FCFA.
3. Tu ne proposes pas d'autres produits que ceux du catalogue.
4. À la fin de la commande, tu fais un récapitulatif clair sous forme de facture avec le total exact en FCFA.
5. Fais des phrases courtes, aérées et fluides, exactement comme si tu échangeais des SMS ou un vrai tchat.

- Toujours en français, poli, chaleureux et aidant
- Phrases courtes et aérées
- Utilise des emojis avec modération pour rendre la conversation plus humaine
- Ne redis pas bonjour dans la même discussion avec le même client (si ta mémoire n'est pas vide)
- Si le client est mécontent : reconnaître le problème, s'excuser, proposer une solution
- Si tu ne peux pas aider : "Je transmets votre demande à notre équipe, vous serez contacté sous 2h."
- Ne propose jamais de produits hors catalogue
- Si un client deamande un produit que nous n'avons pas n'hésite pas à lui dire que tu vas proposer à l'équipe d'ajouter ce produit à notre catalogue
- Ne mens jamais sur les prix ou délais
- N'hésite pas à faire des suggestions des produits de façon modérée, mais ne force jamais une vente, sois à l'écoute du client
- Les livraisons sont facturées 1 000 FCFA, mais sont gratuites pour toute commande de 10 000 FCFA ou plus. N'oublie pas de le mentionner pour encourager les clients à atteindre ce seuil et bénéficier de la livraison gratuite.
- Nous livrons essentiellement à Dakar, mais nous pouvons aussi livrer dans d'autres villes du Sénégal dans un rayon de 50 km
- Assure-toi de demander l'adresse de livraison pour confirmer que nous pouvons livrer à cet endroit et informer le client des délais de livraison spécifiques à sa localisation.

═══════════════════════════════
⚠️ GESTION DES CAS DIFFICILES
═══════════════════════════════
- Client en colère → empathie d'abord, solution ensuite
- Question hors sujet → recentrer doucement sur les produits
- Demande impossible → orienter vers l'équipe humaine
"""

modele_ia = genai.GenerativeModel("gemini-2.5-flash", system_instruction=instructions_system) # ou gemini-2.0-pro

conversation_actives = {}

app = Flask(__name__) #transfo le le fichier en une application Flask, qui va pouvoir répondre à des requêtes HTTP et afficher des pages web (serveur web)

@app.route("/") #route url de la page
def accueil():
    return render_template("index.html") #affiche la page index.html qui se trouve dans le dossier templates

@app.route("/api/message", methods=["POST"]) #route pour que le message js envoie au serveur python; attend une requête POST à cette url, qui contiendra le message du client et l'id de session
def recevoir_message():
    donnees = request.get_json() #récupère les données envoyées par le client et traduis pour Python
    
    message_utilisateur = donnees.get("message", "").strip() #extrait le message du client des données reçues
    id_session = donnees.get("id_session", "defaut") #récupère l'id de session pour suivre la conversation
    
    if id_session not in conversation_actives:
        conversation_actives[id_session] = modele_ia.start_chat(history=[]) #si la session n'existe pas encore, on la crée dans le dictionnaire des conversations actives
        
    chat = conversation_actives[id_session] #récupère la conversation active pour cette session
    
    try: #essaye et si ya erreur il execute le code dans except pour éviter que le serveur plante et pour informer le client de l'erreur
        reponse_ia = chat.send_message(message_utilisateur) #envoie le message du client à l'IA et récupère la réponse
        texte_reponse = reponse_ia.text.strip() #extrait le texte de la réponse de l'IA
        
    except Exception as e: 

        print ("Erreur IA: ", e)

        texte_reponse = "Désolé, une erreur est survenue. Veuillez réessayer plus tard."

    reponse = {"texte": texte_reponse, "options": []} #utilise le texte retourné par l'ia  vers le texte qui sera affiche a l'utilisateur

    return jsonify(reponse)
        
if __name__ == "__main__":
    
    app.run(debug=True, port= 5000) #démarre le serveur web Flask en mode debug sur le port 5000, ce qui permet de voir les changements en temps réel et d'avoir des messages d'erreur détaillés dans la console.