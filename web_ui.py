from flask import Flask, request, jsonify, session, render_template_string
import os

# Υποθέτω έχεις τις παρακάτω λειτουργίες ήδη από chatbot2.py
from chatbot2 import (
    check_lm_studio, load_and_embed_data, ask_lm_studio,
    remove_tonos, clean_lm_response, fallback_contexts
)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Φόρτωση μοντέλου και δεδομένων
embed_model, collection = (None, None)
if check_lm_studio():
    embed_model, collection = load_and_embed_data()
else:
    print("⚠️ LM Studio is not available.")

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="el">
<head>
    <meta charset="UTF-8">
    <title>GreenAirBot</title>
    <style>
       body {
    font-family: 'Segoe UI', sans-serif;
    margin: 0;
    padding: 0;
    background: linear-gradient(to right, #e6f4ea, #f6fff6);
    color: #2c2c2c;
    line-height: 1.6;
}

header {
    background-color: #228B22;
    color: white;
    padding: 1rem 0.5rem;
    text-align: center;
    border-bottom: 5px solid #196619;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

header h1 {
    margin: 0;
    font-size: 2.1rem;
    letter-spacing: 0.5px;
}

header p {
    margin-top: 0.4rem;
    font-size: 1.1rem;
    opacity: 0.95;
}

.container {
    max-width: 900px;
    margin: 1.5rem auto;
    padding: 0.5rem;
}

.features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.2rem;
    margin-top: 1.5rem;
    padding: 1rem;
}

.feature {
    background: #ffffff;
    padding: 1.2rem;
    border-radius: 18px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.feature:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
}

.feature h3 {
    color: #228B22;
    margin-bottom: 0.5rem;
}

/* === CHATBOX STYLE === */

.chatbox {
    margin-top: 1.2rem;
    max-height: 480px;
    overflow-y: auto;
    padding: 1.5rem 2.0rem;
    border: 1px solid #ccdccc;
    border-radius: 15px;
    background: #f4f9f4;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.03);
    width: 85%;
}

.message {
    padding: 0.85rem 1.1rem;
    border-radius: 22px;
    max-width: 75%;
    word-wrap: break-word;
    line-height: 1.5;
    font-size: 0.95rem;
    position: relative;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.user {
    align-self: flex-end;
    background-color: #cce6ff;
    border-bottom-right-radius: 0;
}

.bot {
    align-self: flex-start;
    background-color: #dbf2db;
    border-bottom-left-radius: 0;
}

/* === FORM STYLE === */

form {
    display: flex;
    gap: 1rem;
    margin-top: 1.2rem;
    flex-wrap: wrap;
    justify-content: center;
}

input[type=text] {
    flex: 1 1 auto;
    padding: 0.8rem 1.1rem;
    font-size: 1rem;
    border-radius: 20px;
    border: 1px solid #bbb;
    transition: border-color 0.3s;
}

input[type=text]:focus {
    outline: none;
    border-color: #228B22;
}

button {
    background-color: #228B22;
    color: white;
    border: none;
    padding: 0.8rem 1.3rem;
    font-size: 1rem;
    border-radius: 20px;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.1s ease;
}

button:hover {
    background-color: #1e7a1e;
    transform: scale(1.02);
}

.footer {
    background-color: #228B22;
    color: white;
    padding: 1rem;
    text-align: center;
    margin-top: 3rem;
    font-size: 0.95rem;
}

/* === RESPONSIVE === */

@media (max-width: 600px) {
    header h1 {
        font-size: 1.8rem;
    }

    form {
        flex-direction: column;
    }

    input[type=text],
    button {
        width: 100%;
    }

    .feature {
        text-align: center;
    }
}
    </style>
</head>
<body>
<header>
    <h1>GreenAirBot</h1>
    <p>Έξυπνες Πληροφορίες για Ποιότητα Αέρα, με τη Δύναμη των Ανοιχτών Δεδομένων</p>
</header>
<div class="container">

    <section class="features">
        <div class="feature">
            <h3>Ζωντανός Χάρτης Καθαρού Αέρα</h3>
            <p>Ανακάλυψε τις πιο καθαρές ώρες στο λιμάνι της Θεσσαλονίκης με real-time δεδομένα από τον ΟΛΘ και προγραμμάτισε Smart τις δραστηριότητές σου</p>
        </div>
        <div class="feature">
            <h3>Προστασία Υγείας</h3>
            <p>Ενημερώσου για τις ώρες που μπορείς να αποφύγεις την έκθεση σε υψηλή ρύπανση λόγω ποιότητας του αέρα σε πραγματικό χρόνο (Ιδανικό για άτομα με αναπνευστικά προβλήματα).</p>
        </div>
        <div class="feature">
            <h3>Ανοιχτά Δεδομένα</h3>
            <p>Σύνδεση με τον ΟΛΘ για δεδομένα ποιότητας αέρα σε πραγματικό χρόνο. Ορατοποίησε το αόρατο και ζήσε πιο έξυπνα, πιο καθαρά!</p>
        </div>
    </section>
    <h2>GreenAirBot</h2>

 <form method="POST" action="/">
    <input type="text" name="question" placeholder="Γράψε την ερώτησή σου">
    <button type="submit">Ρώτησε</button>
    <button type="submit" name="clear" value="1" style="background-color:#bbb; color:#000;">🗑 Εκκαθάριση</button>
</form>

    <div class="chatbox" id="chatbox">
        {% for speaker, msg in history %}
            <div class="message {% if speaker == 'Εσύ' %}user{% else %}bot{% endif %}">
                <strong>{{ speaker }}:</strong>
                <p>{{ msg }}</p>
            </div>
        {% endfor %}
    </div>
</div>

<script>
    // Scroll to bottom on page load
    window.onload = function() {
        const chatbox = document.getElementById('chatbox');
        chatbox.scrollTop = chatbox.scrollHeight;
    };
</script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    global embed_model, collection

    if "chat_history" not in session:
        session["chat_history"] = []

    if request.method == "POST":

        # ✅ Έλεγχος για το κουμπί εκκαθάρισης
        if request.form.get("clear"):
            session["chat_history"] = []
            session.modified = True
            return render_template_string(HTML_TEMPLATE, history=[])

        question = request.form.get("question", "").strip()
        answer = ""

        if question:
            clean_q = remove_tonos(question.lower())

            # Έλεγχος για fallback λέξεις-κλειδιά
            fallback_hits = [
                text for keyword, text in fallback_contexts.items()
                if keyword in clean_q
            ]

            if fallback_hits:
                answer = "\n\n".join(fallback_hits)

            elif embed_model and collection:
                embedding = embed_model.encode([f"query: {clean_q}"])[0]
                results = collection.query(query_embeddings=[embedding], n_results=4, include=["documents"])
                context_chunks = results.get("documents", [[]])[0]

                for keyword, fallback_text in fallback_contexts.items():
                    if keyword in clean_q and fallback_text not in context_chunks:
                        context_chunks.append(fallback_text)

                context = "\n".join(context_chunks)
                base_context = ""
                raw_response = ask_lm_studio(clean_q, base_context, context_chunks)
                answer = clean_lm_response(raw_response, base_context, context)

            else:
                answer = "⚠️ Δεν είναι δυνατή η επεξεργασία της ερώτησης αυτή τη στιγμή."

            MAX_HISTORY = 20
            session["chat_history"].append(("Εσύ", question))
            session["chat_history"].append(("GreenAirBot", answer))
            session["chat_history"] = session["chat_history"][-MAX_HISTORY:]
            session.modified = True

        return render_template_string(HTML_TEMPLATE, history=session.get("chat_history", []))

    return render_template_string(HTML_TEMPLATE, history=session.get("chat_history", []))






@app.route("/chat", methods=["POST"])
def chat_api():
    data = request.get_json(force=True)
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "No question provided"}), 400

    clean_q = remove_tonos(question.lower())

    fallback_hits = [text for keyword, text in fallback_contexts.items() if keyword in clean_q]

    if fallback_hits:
        answer = "\n\n".join(fallback_hits)
    else:
        answer = ask_lm_studio(clean_q, "", [])

    return jsonify({"answer": answer})

@app.route("/ws/ws")
def ws_dummy():
    return "WebSocket endpoint not implemented yet", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

