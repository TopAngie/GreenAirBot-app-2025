import requests
import os
import json
import re
from sentence_transformers import SentenceTransformer
from chromadb import Client
from chromadb.config import Settings
import unicodedata


# === Configuration ===
LM_API_URL = "http://10.0.41.186:1234/v1"
MODEL_NAME = "mistral-7b-instruct-v0.3"
EMBED_MODEL_NAME = "intfloat/e5-small"
DATA_FILE = "GreenAirChatBot/airdatafiles3.txt"
COLLECTION_NAME = "greenair_collection"

# === Check if LM Studio is running ===
def check_lm_studio():
    try:
        response = requests.get(f"{LM_API_URL}/models")
        response.raise_for_status()
        models = response.json().get("data", [])
        model_names = [m["id"] for m in models]
        if MODEL_NAME not in model_names:
            print(f"❌ Το μοντέλο '{MODEL_NAME}' δεν είναι φορτωμένο στο LM Studio.")
            print(f"📌 Φορτώστε το μοντέλο από LM Studio και προσπαθήστε ξανά.")
            return False
        print(f"✅ Το LM Studio είναι σε λειτουργία και το μοντέλο είναι φορτωμένο.")
        return True
    except Exception as e:
        print(f"❌ Δεν ήταν δυνατή η σύνδεση με το LM Studio ({LM_API_URL})")
        print(f"📌 Βεβαιώσου ότι είναι ανοιχτό και ενεργοποιημένο το API (port 1234).")
        return False

# === Load and embed data ===
def load_and_embed_data():
    if not os.path.exists(DATA_FILE):
        print(f"❌ Το αρχείο '{DATA_FILE}' δεν βρέθηκε.")
        exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    # 🔹 Διαχωρισμός σε chunks με βάση παραγράφους
    raw_chunks = text.strip().split("\n\n")

    # 🔸 Εφαρμογή "passage:" prefix για κάθε chunk
    chunks = [f"passage: {chunk}" for chunk in raw_chunks]

    embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    embeddings = embed_model.encode(chunks)

    client = Client(Settings(anonymized_telemetry=False))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    all_ids = [f"doc-{i}" for i in range(len(chunks))]
    collection.delete(ids=all_ids)

    for i, chunk in enumerate(chunks):
        collection.add(documents=[chunk], embeddings=[embeddings[i]], ids=[f"doc-{i}"])

    return embed_model, collection
def remove_tonos(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )



fallback_contexts = {
   
        "αυξημενη": (
            "Αυξημένη ρύπανση παρατηρήθηκε στις 08:00 και στις βραδινές ώρες μεταξύ 19:00 και 21:00."
        ),
        "χειροτερη": (
            "Η χειρότερη ώρα ήταν στις 09:00 της 2ης Ιανουαρίου με NOx 236.90 ppb και NO2 57.43 μg/m³."
        ),
        "καθαρότερη": (
            "Η καθαρότερη ώρα καταγράφηκε στις 16:00 της 1ης Ιανουαρίου 2024 με NOx 6.78 ppb και NO2 11.85 μg/m³."
        ),
           
         "λιμανι": (
            "Το λιμάνι της Θεσσαλονίκης είναι σημαντικό επειδή είναι ένας ζωντανός κόμβος μεταφορών και εμπορίου για τη Βόρεια Ελλάδα. "
             "Καθημερινά, φορτηγά, γερανοί και πλοία λειτουργούν αδιάκοπα, συμβάλλοντας στην ανάπτυξη αλλά και στην επιβάρυνση του περιβάλλοντος με ρύπους όπως NO, NOx και NO2. "
             "Τα δεδομένα του ΟΛΘ δείχνουν διακυμάνσεις στη ρύπανση μέσα στη μέρα, και το GreenAirBot χρησιμοποιεί αυτά τα δεδομένα για να προτείνει ώρες καθαρού αέρα για εξωτερικές δραστηριότητες και να δίνει πρακτικές οικολογικές συμβουλές."
        ),
           "greenairbot": (
           "Το GreenAirBot είναι ένα περιβαλλοντικό chatbot βασισμένο σε ανοιχτά δεδομένα ρύπανσης από τον ΟΛΘ. "
           "Ενημερώνει για ρύπους όπως NO, NOx και NO2 και προτείνει ώρες με καθαρότερο αέρα για περπάτημα, ποδήλατο ή άθληση (π.χ. 16:00, 05:00, 17:00). "
           "Επίσης, δίνει συμβουλές όπως αερισμό σπιτιού, χρήση ποδηλάτου, και φυτεύσεις, προωθώντας βιώσιμες επιλογές καθημερινότητας."
        ),
            "ρυπανση": (
            "Στις 09:00 της 2ης Ιανουαρίου παρατηρήθηκαν υψηλότερες τιμές ρύπων (NOx 236.90 ppb, NO2 57.43 μg/m³). "
            "Το GreenAirBot προτείνει αποφυγή εξωτερικών δραστηριοτήτων σε τέτοιες ώρες και ενίσχυση πράσινων συμπεριφορών."
        ),
             "ωρες": (
             "Οι καθαρότερες ώρες ήταν στις 16:00, 05:00 και 17:00, ενώ οι πιο ρυπασμένες ώρες ήταν 08:00, 09:00 και 19:00-21:00. "
             "Προτείνεται εξωτερική δραστηριότητα τις καθαρές ώρες και αποφυγή έντονης άσκησης στις πιο επιβαρυμένες."
        ),
             "βολτα": (
            "Οι καθαρότερες ώρες ήταν στις 16:00, 05:00 και 17:00, ενώ οι πιο ρυπασμένες ώρες ήταν 08:00, 09:00 και 19:00-21:00. "
            "Προτείνεται εξωτερική δραστηριότητα τις καθαρές ώρες και αποφυγή έντονης άσκησης στις πιο επιβαρυμένες."
        ),
            "τρεξιμο": (
            "Για τρέξιμο με καθαρό αέρα και λιγότερη έκθεση σε ρύπους, οι καλύτερες ώρες είναι στις 05:00, 16:00 και 17:00. "
            "Απόφυγε να τρέχεις μεταξύ 08:00-09:00 και 19:00-21:00, όταν τα επίπεδα ρύπανσης είναι υψηλότερα. "
            "Ξεκίνα τη μέρα σου με μια ανάσα καθαρού αέρα ή χαλάρωσε το απόγευμα με ένα τρέξιμο σε πιο καθαρές συνθήκες!"
        ),
            "περπατημα": (
            "Οι καθαρότερες ώρες ήταν στις 16:00, 05:00 και 17:00, ενώ οι πιο ρυπασμένες ώρες ήταν 08:00, 09:00 και 19:00-21:00. "
            "Προτείνεται εξωτερική δραστηριότητα τις καθαρές ώρες και αποφυγή έντονης άσκησης στις πιο επιβαρυμένες."
        ), 
             "αναστροφη":("Η θερμοκρασιακή αναστροφή είναι ένα συνηθισμένο περιβαλλοντικό φαινόμενο, όταν ένα στρώμα θερμού αέρα παγιδεύει τον ψυχρό αέρα κοντά στο έδαφος, εμποδίζοντας τη διάχυση των ρύπων. Ενημερώσου για τους ρύπους NO, NOx και NO2 για να αποφεύγεις την έκθεση όταν τα επίπεδα είναι υψηλά."), 
            
            "φιλικη": (
            "🌱 Υπέροχη ερώτηση! Για να γίνεις πιο φιλική προς το περιβάλλον, μπορείς να ξεκινήσεις με μικρές πράξεις που έχουν μεγάλη σημασία:\n"
            "🚲 Πήγαινε μια βόλτα με το ποδήλατο αντί να πάρεις το αυτοκίνητο,\n"
            "🚌 προτίμησε τη δημόσια συγκοινωνία για να μειώσεις το αποτύπωμα άνθρακα,\n"
            "🌿 ή φύτεψε ένα φυτό — ακόμα κι ένα μικρό βασιλικό στο περβάζι σου φέρνει ζωή και οξυγόνο!\n\n"
            "💚 Κάθε πράξη μετράει.\n"
            "Πες μου, εσύ σήμερα πώς έδειξες την αγάπη σου για τον πλανήτη; 🌍✨"
        ),
           "φιλικος": (
           "🌱 Υπέροχη ερώτηση! Για να γίνεις πιο φιλικός προς το περιβάλλον, μπορείς να ξεκινήσεις με μικρές πράξεις που έχουν μεγάλη σημασία:\n"
           "🚲 Πήγαινε μια βόλτα με το ποδήλατο αντί να πάρεις το αυτοκίνητο,\n"
           "🚌 προτίμησε τη δημόσια συγκοινωνία για να μειώσεις το αποτύπωμα άνθρακα,\n"
           "🌿 ή φύτεψε ένα φυτό — ακόμα κι ένα μικρό βασιλικό στο περβάζι σου φέρνει ζωή και οξυγόνο!\n\n"
           "💚 Κάθε πράξη μετράει.\n"
           "Πες μου, εσύ σήμερα πώς έδειξες την αγάπη σου για τον πλανήτη; 🌍✨"
        ),
          "ποδηλατο":(""),
          "συγκοινωνια":(""),
          "αστικο":(""),
          "λεωφορειο":(""),
          "τρενο":(""),
          "μετρο":(""),
          "φυτο":(""),
          "τραινο":(""),
        
    }

eco_actions = {
    "ποδηλατο": 5,
    "συγκοινωνια": 5,
    "αστικο": 5,
    "λεωφορειο": 5,
    "τρενο": 5,
    "μετρο": 5,
    "φυτο": 5,
    "τραινο": 5
}

def calculate_eco_points(text):
    text = remove_tonos(text.lower())
    total_points = 0
    matched = []

    for keyword, points in eco_actions.items():
        if keyword in text:
            total_points += points
            matched.append(keyword)

    return total_points, matched

def get_fallback_answer(question):
    question_norm = remove_tonos(question.lower())
    for key, answer in fallback_contexts.items():
        if key in question_norm:
            return answer
    return None




def answer_question(question, base_context, context_chunks):
    # Πρώτα fallback απάντηση
    fallback_answer = get_fallback_answer(question)
    if fallback_answer:
        return fallback_answer

    # Αν δεν υπάρχει fallback, χρησιμοποίησε μόνο τα context chunks από αναζήτηση
    if not context_chunks:
        # Αν δεν βρέθηκαν σχετικά chunks, δώσε ένα μήνυμα αντί απάντησης με fallback
        return "Σε παρακαλώ κάνε μια πιο συγκεκριμένη ερώτηση."

    return ask_lm_studio(question, base_context, context_chunks)


# === Call LM Studio ===
def ask_lm_studio(question,base_context, context_chunks):
    
   
    context =  base_context + "\n\n" + "\n".join([chunk for chunk in context_chunks if chunk])


    prompt = (
        "Απάντησε αποκλειστικά και μόνο στα ελληνικά. Μη χρησιμοποιήσεις αγγλικές λέξεις.\n"
        "Είσαι το GreenAirBot.\n"
        "Απάντησε αποκλειστικά με βάση τα δεδομένα από το κείμενο, χωρίς εικασίες ή γενικότητες.\n"
        "Όταν η ερώτηση αφορά εξωτερική δραστηριότητα, δώσε συγκεκριμένες ώρες καθαρού αέρα.\n"
        "Εαν η ερώτηση δεν έχει σχέση με το περιβάλλον, την ρύπανση, το GreenAirBot, το λιμάνι, την υγεία, το άσθμα, τον αέρα ή τα open data, απάντησε 'Σε παρακαλώ κάνε μια πιο συγκεκριμένη ερώτηση.'"
        "Δώσε σαφή, αναλυτική και πρακτική απάντηση προς το περιβάλλον, αυστηρά με βάση το κείμενο.\n"
        "Αν η ερώτηση περιέχει ορθογραφικά ή φραστικά λάθη ή είναι εντελώς ασαφής και δεν μπορείς να βγάλεις νόημα, απάντησε: 'Σε παρακαλώ κάνε μια πιο συγκεκριμένη ερώτηση.'\n"
        "Αν δεν μπορείς να απαντήσεις με σαφήνεια στην ερώτηση του χρήστη με βάση τα δεδομένα, πες επίσης: 'Σε παρακαλώ κάνε μια πιο συγκεκριμένη ερώτηση.'\n"
        "Αν η ερώτηση αφορά το πώς βοηθάει το GreenAirBot, εξήγησε με απλό τρόπο τις λειτουργίες του και πώς συμβάλλει στην υγεία και το περιβάλλον.\n\n"
        f"{context}\n\n"
        f"Ερώτηση: {question}\n\n"
        "Απάντηση:"
    )

 

    



    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "top_p": 0.9,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
        "max_tokens": 1000,
        "stream": False
    }

    try:
        response = requests.post(f"{LM_API_URL}/chat/completions", headers={"Content-Type": "application/json"}, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        full_text = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        sentences = re.split(r'(?<=[.!;])\s+', full_text)
        for sentence in sentences:
            if len(sentence.split()) > 3 and sentence[-1] in ".;":
                return sentence.strip()
        return sentences[0] if sentences else "⚠️ Δεν βρέθηκε σαφής απάντηση."
    except Exception as e:
        print("❌ Σφάλμα στη σύνδεση με το LM Studio:", e)
        return "⚠️ Δεν ήταν δυνατή η επεξεργασία της ερώτησης."



# === Main chatbot loop ===
def chatbot_loop(embed_model, collection):
    print("\n💬 GreenAirBot: Μπορείς να ρωτήσεις για την ατμοσφαιρική ρύπανση στο λιμάνι Θεσσαλονίκης.")
      
    while True:
        question = input("\n❓ Ερώτηση (ή 'exit' για έξοδο): ")
        if question.lower() == "exit":
            print("👋 Έξοδος.")
            break

        question_norm = remove_tonos(question.lower())

        # Πρώτα fallback απάντηση
        fallback_answer = get_fallback_answer(question_norm)
        if fallback_answer:
            print("➡️ Απάντηση:", fallback_answer)
            continue
 

          # === Προκαθορισμένες απαντήσεις για ερωτήσεις σχετικά με το GreenAirBot
        predefined_qs = [
            "πως με βοηθαει το greenairbot",
            "πως το greenairbot βοηθαει την υγεια μου",
            "πως το greenairbot προστατευει την υγεια μου",
            "γιατι να χρησιμοποιησω το greenairbot",
            "greenairbot",
            "τι ειναι το greenairbot",
            "τι ειναι greenairbot",
            "τι κανει το greenairbot",
            "πως λειτουργει το greenairbot"
        ]
        clean_question = remove_tonos(question).lower().strip()
        if any(phrase in clean_question for phrase in predefined_qs):
            print("➡️ Απάντηση:", "Το GreenAirBot είναι ένα πρόγραμμα που σου δίνει καθημερινά πληροφορίες για την ποιότητα του αέρα στην περιοχή σου, χρησιμοποιώντας ανοιχτά περιβαλλοντικά δεδομένα. Σε ενημερώνει για ρύπους όπως το NO, το NOx και το NO2, ώστε να αποφεύγεις την έκθεση σε υψηλά επίπεδα ρύπανσης. Επίσης, σου προσφέρει πρακτικές συμβουλές για να προστατεύεις την υγεία σου και να συμβάλλεις σε ένα πιο καθαρό και υγιεινό περιβάλλον.")
            continue
        # === Κανονική αναζήτηση context
        query_embedding = embed_model.encode([f"query: {question}"])[0]
        results = collection.query(query_embeddings=[query_embedding], n_results=4, include=["documents"])
        context_chunks = results.get("documents", [[]])[0]

        question = remove_tonos(question)

        

        # === Ανίχνευση λέξεων-κλειδιών και προσθήκη fallback
        question_lower = question.lower()

      
        fallback_added = []
        for keyword, fallback_text in fallback_contexts.items():
            if keyword in question_lower and fallback_text not in context_chunks:
                context_chunks.append(fallback_text)
                fallback_added.append(keyword)

        # === Συνένωση context
        context = "\n".join(context_chunks)

        # === Debug εμφανίσεων
        print("\n📄 Χρησιμοποιείται το εξής context:")
        print("-" * 40)
        print(context)
        print("-" * 40)
        if fallback_added:
            print(f"🧩 Προστέθηκαν fallback context για λέξεις: {', '.join(fallback_added)}")
        base_context = ""        

        # === Ερώτηση στο LM Studio
        answer = ask_lm_studio(question_lower, base_context, context_chunks)





    print("➡️ Απάντηση:", answer)
def clean_lm_response(response, base_context, context):
    # Συντακτικές διορθώσεις
    substitutions = {
        r'δώσοντας σε καθοδηγία': 'παρέχοντάς σου καθοδήγηση',
        r'GreenAirBot βοηθάει': 'Το GreenAirBot βοηθάει',
        r'πρόσθετες': 'πληροφορίες',
        r'δίν.*?σε': 'σου δίνει',
    }
    for pattern, replacement in substitutions.items():
        response = re.sub(pattern, replacement, response, flags=re.IGNORECASE)

    # Προσθήκη ελλείπουσας πληροφορίας αν δεν περιλαμβάνεται
    if 'ρύπους' not in response and 'NO2' in context:
        response += " Ενημερώσου για τους ρύπους NO, NOx και NO2 για να αποφεύγεις την έκθεση όταν τα επίπεδα είναι υψηλά."
    
    # Βελτίωση σύντομων ή επαναληπτικών απαντήσεων
    if len(response.split()) < 8:
        response += " Σου δίνει πρακτικές συμβουλές για να προστατεύεις την υγεία σου και να μειώσεις την έκθεσή σου στους ρύπους."

    return response.strip()

# === Run everything ===
if __name__ == "__main__":
    if check_lm_studio():
        embed_model, collection = load_and_embed_data()
        chatbot_loop(embed_model, collection)

