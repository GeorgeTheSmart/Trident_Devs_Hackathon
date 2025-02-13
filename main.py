from flask import Flask, request, jsonify
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import json

app = Flask(__name__)

model = OllamaLLM(model='llama3')
template = '''
    You are a helpful assistant for "The Shop" located in SRM IST Vadapalani Campus, Tamil Nadu, Chennai.
    Answer customer questions about products, store hours, policies, and recommendations.
    If a customer asks about a product, provide its availability, price, quantity, and exact location in the store.
    If a customer requests all items, list all available products with their sections.
    Provide friendly and professional responses.
    Always display available commands:
    - 'view all items' → List all products.
    - 'find [product name]' → Check availability, location, and quantity.
    - 'store hours' → Get store timings.
    - 'exit' → Quit the chat.
    Autocomplete incomplete commands or keywords.

    Conversation History:
    {context}

    Customer Question: {question}

    Shop Assistant Response: 
'''
prompt = ChatPromptTemplate.from_template(template=template)
chain = prompt | model

products_db = [
    {"sectionId": "B1", "categoryName": "Smartphones & Tablets", "products": [
        {"name": "iPhone 15 Pro", "brand": "Apple", "price": 99999, "quantity": 5, "position": "Counter 1, Shelf A", "imageUrl": "/B/b1/1.jpeg"},
        {"name": "Galaxy S23 Ultra", "brand": "Samsung", "price": 124999, "quantity": 3, "position": "Counter 1, Shelf B", "imageUrl": "/B/b1/2.jpeg"},
        {"name": "Pixel 8 Pro", "brand": "Google", "price": 89999, "quantity": 2, "position": "Counter 1, Shelf C", "imageUrl": "/B/b1/3.jpeg"}
    ]},
    {"sectionId": "B2", "categoryName": "Laptops & Computers", "products": [
        {"name": "MacBook Air M2", "brand": "Apple", "price": 114999, "quantity": 4, "position": "Counter 2, Shelf A", "imageUrl": "/B/b2/1.jpeg"},
        {"name": "Dell XPS 15", "brand": "Dell", "price": 149999, "quantity": 2, "position": "Counter 2, Shelf B", "imageUrl": "/B/b2/2.jpeg"}
    ]}
]

def find_product(product_name):
    for section in products_db:
        for product in section["products"]:
            if product_name.lower() in product["name"].lower():
                return {"message": f"{product['name']} by {product['brand']} is available in section {section['sectionId']} under {section['categoryName']}. Price: ₹{product['price']}. Quantity available: {product['quantity']}. Position: {product['position']}", "imageUrl": product['imageUrl']}
    return {"message": "Sorry, the product is not available."}

def list_all_products():
    products = []
    for section in products_db:
        for product in section["products"]:
            products.append({"name": product["name"], "brand": product["brand"], "price": product["price"], "quantity": product["quantity"], "position": product["position"], "section": section["sectionId"], "imageUrl": product["imageUrl"]})
    return {"products": products}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("message", "").strip()
    
    if user_input.lower() == 'view all items':
        return jsonify(list_all_products())
    elif user_input.lower().startswith('find'):
        product_name = user_input[5:].strip()
        return jsonify(find_product(product_name))
    elif user_input.lower() == 'store hours':
        return jsonify({"message": "The store is open from 9 AM to 9 PM every day."})
    else:
        result = chain.invoke({'context': "", 'question': user_input})
        return jsonify({"message": result})

if __name__ == '__main__':
    app.run(debug=True)
