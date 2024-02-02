def initializeDB(products_collection, orders_collection):
    orders_collection.delete_many({})
    products_collection.delete_many({})
    productData = [{"_id":1, "Name":"Speaker", "Price":2999, "Quantity":7},
                {"_id":2, "Name":"Earbud", "Price":6999, "Quantity":4},
                {"_id":3, "Name":"Watch", "Price":13990, "Quantity":6},
                {"_id":4, "Name":"Headphone", "Price":26999, "Quantity":1},
                {"_id":5, "Name":"Monitor", "Price":39999, "Quantity":5},
                {"_id":6, "Name":"Mouse", "Price":999, "Quantity":28},
                {"_id":7, "Name":"Keyboard", "Price":2890, "Quantity":7},
                {"_id":8, "Name":"Extension", "Price":799, "Quantity":30},
                {"_id":9, "Name":"Cooling Pad", "Price":1200, "Quantity":2},
                {"_id":10, "Name":"WebCam", "Price":1500, "Quantity":9},
                ]
    products_collection.insert_many(productData)
    print("Inserted Dummy Data to DB")