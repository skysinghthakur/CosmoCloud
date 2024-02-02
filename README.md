# CosmoCloud Backend Readme

## Project Overview

Welcome to the CosmoCloud Backend project! This project is a FastAPI-based application that interacts with MongoDB to manage product details and orders. Before you begin, please follow the instructions below to set up your environment.

## Prerequisites

- MongoDB version 7.0.5
- Python version 3.10 or above

## Setup Instructions

1. **Install MongoDB:**

   Please install MongoDB version 7.0.5 on your system. You can download it from the [official MongoDB website](https://www.mongodb.com/try/download/community).

2. **Create a Python Virtual Environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment:**

   - On Windows:

     ```bash
     .\venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

4. **Install Requirements:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Check MongoDB Configuration:**

   - Ensure that MongoDB is running on `localhost:27017`.
   - If not, update the `main.py` file (line 11) with the appropriate `MongoClient` configuration.

6. **Database Configuration:**

   - Make sure there is no database named "Product" to ensure a smooth experience.
   - If needed, change the database name in the `main.py` file (line 12).

7. **Run the FastAPI App:**

   ```bash
   python main.py
   ```

8. **Access the Swagger Documentation:**

   Open your web browser and go to `http://127.0.0.1:8000/docs`.

## Swagger API Documentation

- **GET API: `products`**

  - Parameters:
    - `limit` (default: 10)
    - `offset` (default: 0)
    - `min_price` (optional)
    - `max_price` (optional)

  - Example Request:
    ```json
    {
      "limit": 10,
      "offset": 0,
      "min_price": 8000,
      "max_price": 30000
    }
    ```

  - Example Response:
    ```json
    {
      "data": [
        {
          "_id": 3,
          "Name": "Watch",
          "Price": 13990,
          "Quantity": 6
        },
        {
          "_id": 4,
          "Name": "Headphone",
          "Price": 26999,
          "Quantity": 1
        }
      ],
      "page": {
        "limit": 10,
        "nextOffset": null,
        "prevOffset": null,
        "total": 2
      }
    }
    ```

- **POST API: `createOrder`**

  - Example Request:
    ```json
    {
      "items": [
        {
          "productId": 2,
          "boughtQuantity": 1
        },
        {
          "productId": 3,
          "boughtQuantity": 1
        }
      ],
      "userAddress": {
        "city": "city1",
        "country": "country1",
        "zipCode": 10092
      }
    }
    ```

  - Example Response:
    ```json
    {
      "_id": "<some objectid>",
      "createdOn": "2024-02-02T22:22:59.557566",
      "items": [
        {
          "productId": 2,
          "boughtQuantity": 1,
          "totalAmount": 6999
        },
        {
          "productId": 3,
          "boughtQuantity": 1,
          "totalAmount": 13990
        }
      ],
      "userAddress": {
        "city": "city1",
        "country": "country1",
        "zipCode": 10092
      },
      "totalAmount": 20989
    }
    ```

## Additional Information

- The product details are stored in the 'ProductDetails' collection.
- The order details are stored in the 'OrderDetails' collection.
- When the server is restarted, both collections are emptied and repopulated with sample data.
- To edit or add more data, refer to the 'OperationsOnDB.py' file or use MongoDB tools (Compass, Shell, etc.).
