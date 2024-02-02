from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import uvicorn, OperationsOnDB

app = FastAPI()

client = MongoClient('mongodb://localhost:27017/')
db = client['Product']
products_collection = db['ProductDetails']
orders_collection = db['OrdersDetails']

@app.get("/products/")
async def list_products(
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,):

    query = {}
    if min_price is not None or max_price is not None:
        query["Price"] = {}
    if min_price is not None:
        query["Price"]["$gte"] = min_price
    if max_price is not None:
        query["Price"]["$lte"] = max_price

    pipeline = [
        {'$match': query},
        {'$facet': {
            'data': [{'$skip': offset},
                     {'$limit': limit}],
            'totalCount': [{'$count': 'total'}]
        }}
    ]

    results = list(products_collection.aggregate(pipeline))

    if not results:
        return {'data':[],'page':{'limit': limit, 'nextOffset': None, 'prevOffset': None, 'total': 0}}
    
    data = results[0]['data']

    totalCount = results[0]['totalCount'][0]['total'] if results[0]['totalCount'] else 0
    nextOffset = offset + limit if totalCount > offset + limit else None
    prevOffset = offset - limit if offset - limit >= 0 else None

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

@app.post("/createOrder/")
async def createOrder(order: Order):
    created_on = datetime.now().isoformat()

    total_amount = 0.0
    ordered_items = []

    for item in order.items:
        product_id = item.productId
        product = products_collection.find_one({"_id": product_id})
        if product is None:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        
        price = product["Price"]

        if product['Quantity'] < item.boughtQuantity:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} has only {product['Quantity']} quatity left")
        
        total_amount += price * item.boughtQuantity 

        products_collection.update_one({"_id": product_id}, {"$inc": {"Quantity": -item.boughtQuantity}})

        ordered_items.append({
            "productId": product_id,
            "boughtQuantity": item.boughtQuantity,
            "totalAmount": price * item.boughtQuantity
        })

    response = {
        "_id": str(ObjectId()),
        "createdOn": created_on,
        "items": ordered_items,
        "userAddress": dict(order.userAddress),
        "totalAmount": total_amount
    }
    orders_collection.insert_one(response)
    return response

if __name__ == "__main__":
    OperationsOnDB.initializeDB(products_collection, orders_collection)
    uvicorn.run(app)
