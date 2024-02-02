# Importing necessary modules and libraries
from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import uvicorn, OperationsOnDB

# Initializing FastAPI app
app = FastAPI()

# Connecting to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Product']
products_collection = db['ProductDetails']
orders_collection = db['OrdersDetails']

# API endpoint to list products with optional filters
@app.get("/products/")
async def list_products(
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,):

    # Building MongoDB query based on optional filters
    query = {}
    if min_price is not None or max_price is not None:
        query["Price"] = {}
    if min_price is not None:
        query["Price"]["$gte"] = min_price
    if max_price is not None:
        query["Price"]["$lte"] = max_price

    # MongoDB aggregation pipeline to apply filters and paginate results
    pipeline = [
        {'$match': query},
        {'$facet': {
            'data': [{'$skip': offset},
                     {'$limit': limit}],
            'totalCount': [{'$count': 'total'}]
        }}
    ]

    # Executing the aggregation pipeline
    results = list(products_collection.aggregate(pipeline))

    # Handling empty results
    if not results:
        return {'data':[],'page':{'limit': limit, 'nextOffset': None, 'prevOffset': None, 'total': 0}}
    
    # Extracting relevant information from MongoDB results
    data = results[0]['data']
    totalCount = results[0]['totalCount'][0]['total'] if results[0]['totalCount'] else 0
    nextOffset = offset + limit if totalCount > offset + limit else None
    prevOffset = offset - limit if offset - limit >= 0 else None

    # Creating and returning the response
    response = {
        'data': data,
        'page': {
            'limit': limit,
            'nextOffset': nextOffset,
            'prevOffset': prevOffset,
            'total': totalCount
        }
    }
    return response

# Define Pydantic models for request payload validation
class Item(BaseModel):
    productId: int
    boughtQuantity: int

class UserAddress(BaseModel):
    city: str
    country: str
    zipCode: int

class Order(BaseModel):
    items: List[Item]
    userAddress: UserAddress

# API endpoint to create an order
@app.post("/createOrder/")
async def createOrder(order: Order):
    # Getting the current timestamp
    created_on = datetime.now().isoformat()

    total_amount = 0.0
    ordered_items = []

    # Processing each item in the order
    for item in order.items:
        product_id = item.productId
        # Retrieving product details from MongoDB
        product = products_collection.find_one({"_id": product_id})
        if product is None:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        
        # Validating available quantity for the product
        if product['Quantity'] < item.boughtQuantity:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} has only {product['Quantity']} quantity left")
        
        # Calculating total amount for the item
        price = product["Price"]
        total_amount += price * item.boughtQuantity 

        # Updating product quantity in MongoDB
        products_collection.update_one({"_id": product_id}, {"$inc": {"Quantity": -item.boughtQuantity}})

        # Adding item details to the ordered_items list
        ordered_items.append({
            "productId": product_id,
            "boughtQuantity": item.boughtQuantity,
            "totalAmount": price * item.boughtQuantity
        })

    # Creating the response object
    response = {
        "_id": str(ObjectId()),
        "createdOn": created_on,
        "items": ordered_items,
        "userAddress": dict(order.userAddress),
        "totalAmount": total_amount
    }

    # Inserting the order details into MongoDB
    orders_collection.insert_one(response)
    return response

# Initializing the MongoDB collections with sample data
if __name__ == "__main__":
    OperationsOnDB.initializeDB(products_collection, orders_collection)
    # Running the FastAPI app using uvicorn
    uvicorn.run(app)
