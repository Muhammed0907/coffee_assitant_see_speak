from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = 'data.json'
FIELDS = ['prompt', 'greetings', 'suggestions', 'product_name']

def load_data():
    """Load data from JSON file"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    """Save data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/products', methods=['POST'])
def create_product():
    """Create a new product entry"""
    data = request.get_json()
    
    # Validate required fields
    if not all(field in data for field in FIELDS):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check for existing product
    existing_data = load_data()
    if any(p['product_name'].lower() == data['product_name'].lower() for p in existing_data):
        return jsonify({'error': 'Product already exists'}), 400
    
    existing_data.append(data)
    save_data(existing_data)
    return jsonify(data), 201

@app.route('/products', methods=['GET'])
def get_all_products():
    """Get all products"""
    data = load_data()
    return jsonify(data)

@app.route('/products/<product_name>', methods=['GET'])
def get_product(product_name):
    """Get a specific product"""
    data = load_data()
    product = next((p for p in data if p['product_name'].lower() == product_name.lower()), None)
    if product:
        return jsonify(product)
    return jsonify({'error': 'Product not found'}), 404

@app.route('/products/<old_name>', methods=['PUT'])
def update_product(old_name):
    """Update a product"""
    new_data = request.get_json()
    data = load_data()
    
    # Find product index
    index = next((i for i, p in enumerate(data) if p['product_name'].lower() == old_name.lower()), None)
    if index is None:
        return jsonify({'error': 'Product not found'}), 404
    
    # Check if new name exists
    if 'product_name' in new_data:
        new_name = new_data['product_name']
        if any(p['product_name'].lower() == new_name.lower() for p in data):
            return jsonify({'error': 'New product name already exists'}), 400
    
    # Update fields
    for key in FIELDS:
        if key in new_data:
            data[index][key] = new_data[key]
    
    save_data(data)
    return jsonify(data[index])

@app.route('/products/<product_name>', methods=['DELETE'])
def delete_product(product_name):
    """Delete a product"""
    data = load_data()
    new_data = [p for p in data if p['product_name'].lower() != product_name.lower()]
    
    if len(new_data) == len(data):
        return jsonify({'error': 'Product not found'}), 404
    
    save_data(new_data)
    return jsonify({'message': 'Product deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)