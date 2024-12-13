from flask import Flask, request, jsonify, render_template
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import re
import difflib

app = Flask(__name__)

# shelf data
shelf_data = {
    "apple": "Shelf 1",
    "banana": "Shelf 2",
    "carrot": "Shelf 3",
    "detergent": "Shelf 4",
    "egg": "Shelf 5",
    "bread": "Shelf 6",
    "milk": "Shelf 7",
    "cheese": "Shelf 8",
    "butter": "Shelf 9",
    "yogurt": "Shelf 10",
    "orange": "Shelf 11",
    "grape": "Shelf 12",
    "strawberry": "Shelf 13",
    "blueberry": "Shelf 14",
    "watermelon": "Shelf 15",
    "tuna": "Shelf 16",
    "salmon": "Shelf 17",
    "chicken": "Shelf 18",
    "beef": "Shelf 19",
    "pork": "Shelf 20",
    "lettuce": "Shelf 21",
    "spinach": "Shelf 22",
    "cabbage": "Shelf 23",
    "potato": "Shelf 24",
    "onion": "Shelf 25",
    "garlic": "Shelf 26",
    "ginger": "Shelf 27",
    "tomato": "Shelf 28",
    "cucumber": "Shelf 29",
    "pepper": "Shelf 30",
    "mushroom": "Shelf 31",
    "zucchini": "Shelf 32",
    "eggplant": "Shelf 33",
    "pasta": "Shelf 34",
    "rice": "Shelf 35",
    "flour": "Shelf 36",
    "sugar": "Shelf 37",
    "salt": "Shelf 38",
    "pepper": "Shelf 39",
    "olive oil": "Shelf 40",
    "vinegar": "Shelf 41",
    "shampoo": "Shelf 42",
    "conditioner": "Shelf 43",
    "soap": "Shelf 44",
    "toothpaste": "Shelf 45",
    "toilet paper": "Shelf 46",
    "paper towels": "Shelf 47",
    "dish soap": "Shelf 48",
    "laundry detergent": "Shelf 49",
    "cleaning spray": "Shelf 50"
}


# Store the conversation state
conversation_state = {
    "items": [],
    "invalid_items": []
}

# Path to the static folder where PDF will be stored
static_folder = os.path.join(os.getcwd(), 'static')
if not os.path.exists(static_folder):
    os.makedirs(static_folder)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message'].lower().strip()
    response = ""

    greetings = ["hi", "hello", "hey"]
    farewells = ["bye", "goodbye", "that's it", "that's", "finish", "done", "no", "nope"]
    thanks = ["thanku", "thanx", "thank you", "thanks", "ok"]
    stop_words = ["i", "want", "to", "buy", "need", "where", "is", "are", "the", "item", "and", "a", "an", "mean", "can","find", "shelf", "shelves", "how", "get"]

    if user_input in greetings:
        response = "Hello! How can I assist you with your shopping today?"
    elif any(word in user_input for word in farewells):
        shelves = {item: shelf_data.get(item, "Not found") for item in conversation_state["items"]}
        response = "Thank you for chatting with me! Here are the shelf locations for your items:\n"
        response += "\n".join([f"{item}: {shelf}" for item, shelf in shelves.items()])
        response += "\n\nClick the button below to download your shopping list PDF."

        # Generate the PDF and save in the static folder
        pdf_filename = "shopping_list.pdf"
        pdf_path = os.path.join(static_folder, pdf_filename)
        generate_pdf(shelves, pdf_path)

        # Clear conversation state
        conversation_state["items"].clear()
        conversation_state["invalid_items"].clear()

        return jsonify({"response": response, "pdf_path": f"/static/{pdf_filename}", "summary": shelves})
    elif any(word in user_input for word in thanks):
        response = "You're welcome! Is there anything else you would like to buy?"
    else:
        # Extract items and check against shelf_data
        items_requested = extract_items(user_input, stop_words)

        if items_requested:
            valid_items = []
            invalid_items = []

            for item in items_requested:
                normalized_item = normalize_item(item)
                if normalized_item in shelf_data:
                    valid_items.append(normalized_item)
                else:
                    invalid_items.append(item)

            if valid_items:
                response = get_shelf_numbers(valid_items)
                conversation_state["items"].extend(valid_items)

            if invalid_items:
                response += f"\n\nI'm sorry, we don't have '{', '.join(invalid_items)}' in our market. Is there anything else you would like to buy?"
                conversation_state["invalid_items"].extend(invalid_items)

            if not valid_items and not invalid_items:
                response = "I'm sorry, I didn't understand what you're looking for. Could you please specify the items again?"
        else:
            # Check if the user mentioned an invalid item from previous interactions
            if user_input in conversation_state["invalid_items"]:
                response = f"I'm sorry, we still don't have '{user_input}' in our market."
            else:
                response = "I'm sorry, I didn't understand what you're looking for. Could you please specify the items again?"

    return jsonify({"response": response})

def extract_items(user_input, stop_words):
    # Use regex to split user input into words and handle punctuation
    words = re.findall(r'\b\w+\b', user_input)
    items = []
    for word in words:
        if word not in stop_words:
            normalized_word = normalize_item(word)
            items.append(normalized_word)
    return items

def normalize_item(item):
    # Normalize items to singular form by removing common plural suffixes
    if item.endswith('ies'):
        item = item[:-3] + 'y'
    elif item.endswith('es'):
        item = item[:-2]
    elif item.endswith('s') and not item.endswith('ss'):
        item = item[:-1]

    # Use difflib to find the closest match in shelf_data
    closest_match = difflib.get_close_matches(item, shelf_data.keys(), n=1, cutoff=0.8)
    return closest_match[0] if closest_match else item

def generate_pdf(shelves, pdf_path):
    pdf = canvas.Canvas(pdf_path, pagesize=letter)
    pdf.drawString(100, 750, "Shelf Locations")
    y = 700
    for item, shelf in shelves.items():
        pdf.drawString(100, y, f"{item}: {shelf}")
        y -= 20
    pdf.save()

def get_shelf_numbers(items):
    shelves = {item: shelf_data.get(item, "Not found") for item in items}
    response = "You can find\n\n"
    response += "\n".join([f"{item} in {shelf}" for item, shelf in shelves.items()])
    response += ".\n\nIs there anything else you would like to buy?"
    return response

if __name__ == '__main__':
    app.run(debug=True)
