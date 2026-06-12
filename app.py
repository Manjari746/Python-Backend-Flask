from flask import Flask,jsonify, request
app = Flask(__name__)

products = [
    {"id": 1, "name": 'Keyboard', "price":89.99 },
    {"id":2, "name": 'Mouse', "price":29.34},
    {"id":3, "name": 'Printer', "price":100}]
@app.route('/')
def home():
    return jsonify({"message":"Hello, from flask server!"})

# retrieving information from server 
@app.route('/products', methods=["GET"])
def get_products():
    return jsonify(products)

# sending data back to server 
@app.route('/products', methods = ["POST"])
def add_products():
    data = request.get_json() #firstly parsing incoming json 
    new_product = {
        "id" : len(products)+1,
        "name": data.get("name"),
        "price": data.get("price")
    }
    products.append(new_product)
    return jsonify({"message": "product has been added!", "product": new_product}) , 201

if __name__ == "__main__":
    app.run(debug=True)