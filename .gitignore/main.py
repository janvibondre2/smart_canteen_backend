from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
from dotenv import load_dotenv
from jose import jwt
from pydantic import BaseModel
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("URL:", SUPABASE_URL)
print("KEY exists:", SUPABASE_KEY is not None)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Smart Canteen API")


@app.get("/")
def home():
    return {
        "message": "Smart Canteen Backend is running"
    }


@app.get("/categories")
def get_categories():
    response = supabase.table("categories").select("*").execute()
    return response.data
@app.get("/food-items")
def get_food_items():
    response = supabase.table("food_items").select("*").execute()

    return response.data

@app.get("/food-items/search/{keyword}")
def search_food_items(keyword: str):
    response = (
        supabase
        .table("food_items")
        .select("*")
        .ilike("name", f"%{keyword}%")
        .execute()
    )

    return response.data

@app.get("/food-items/category/{category_id}")
def get_food_by_category(category_id: int):
    response = (
        supabase
        .table("food_items")
        .select("*")
        .eq("category_id", category_id)
        .execute()
    )

    return response.data

@app.get("/cart/{user_id}")
def get_cart(user_id: str):
    # Find the user's cart
    cart_response = (
        supabase
        .table("cart")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    if not cart_response.data:
        return {
            "message": "Cart is empty"
        }

    cart_id = cart_response.data[0]["id"]

    # Get items inside the cart
    items_response = (
        supabase
        .table("cart_items")
        .select("*")
        .eq("cart_id", cart_id)
        .execute()
    )

    return {
        "cart_id": cart_id,
        "items": items_response.data
    }

@app.post("/cart/{user_id}/items")
def add_to_cart(user_id: str, food_item_id: int, quantity: int = 1):

    # Find user's cart
    cart_response = (
        supabase
        .table("cart")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    # If cart doesn't exist, create one
    if not cart_response.data:
        new_cart = (
            supabase
            .table("cart")
            .insert({
                "user_id": user_id
            })
            .execute()
        )

        cart_id = new_cart.data[0]["id"]

    else:
        cart_id = cart_response.data[0]["id"]

    # Add food item
    item_response = (
        supabase
        .table("cart_items")
        .insert({
            "cart_id": cart_id,
            "food_item_id": food_item_id,
            "quantity": quantity
        })
        .execute()
    )

    return {
        "message": "Item added to cart",
        "item": item_response.data
    }

@app.put("/cart/items/{item_id}")
def update_cart_item(item_id: int, quantity: int):
    response = (
        supabase
        .table("cart_items")
        .update({
            "quantity": quantity
        })
        .eq("id", item_id)
        .execute()
    )

    return {
        "message": "Cart item updated",
        "item": response.data
    }

@app.delete("/cart/items/{item_id}")
def remove_cart_item(item_id: int):
    response = (
        supabase
        .table("cart_items")
        .delete()
        .eq("id", item_id)
        .execute()
    )

    return {
        "message": "Item removed from cart"
    }

@app.post("/checkout/{user_id}")
def checkout(user_id: str, pickup_time: str):

    # 1. Find user's cart
    cart_response = (
        supabase
        .table("cart")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    if not cart_response.data:
        return {
            "message": "Cart not found"
        }

    cart_id = cart_response.data[0]["id"]

    # 2. Get cart items
    items_response = (
        supabase
        .table("cart_items")
        .select("*")
        .eq("cart_id", cart_id)
        .execute()
    )

    cart_items = items_response.data

    if not cart_items:
        return {
            "message": "Cart is empty"
        }

    total_amount = 0
    order_items = []

    # 3. Get food details and calculate total
    for item in cart_items:

        food_response = (
            supabase
            .table("food_items")
            .select("*")
            .eq("id", item["food_item_id"])
            .execute()
        )

        if not food_response.data:
            return {
                "message": f"Food item {item['food_item_id']} not found"
            }

        food = food_response.data[0]

        if not food["available"]:
            return {
                "message": f"{food['name']} is not available"
            }

        quantity = item["quantity"]
        price = float(food["price"])

        total_amount += price * quantity

        order_items.append({
            "food_item_id": food["id"],
            "quantity": quantity,
            "price": price
        })

    # 4. Create order
    order_response = (
        supabase
        .table("orders")
        .insert({
            "user_id": user_id,
            "total_amount": total_amount,
            "pickup_time": pickup_time,
            "payment_status": "PENDING",
            "order_status": "PLACED"
        })
        .execute()
    )

    order = order_response.data[0]
    order_id = order["id"]

    # 5. Add order items
    for item in order_items:
        supabase.table("order_items").insert({
            "order_id": order_id,
            "food_item_id": item["food_item_id"],
            "quantity": item["quantity"],
            "price": item["price"]
        }).execute()

    # 6. Create payment record
    supabase.table("payments").insert({
        "order_id": order_id,
        "amount": total_amount,
        "payment_method": "TEST",
        "payment_status": "PENDING"
    }).execute()

    # 7. Clear cart
    supabase.table("cart_items").delete().eq(
        "cart_id", cart_id
    ).execute()

    return {
        "message": "Order placed successfully",
        "order_id": order_id,
        "total_amount": total_amount,
        "pickup_time": pickup_time,
        "order_status": "PLACED",
        "payment_status": "PENDING"
    }

@app.post("/payment/{order_id}")
def process_payment(order_id: int):

    # Find payment for this order
    payment_response = (
        supabase
        .table("payments")
        .select("*")
        .eq("order_id", order_id)
        .execute()
    )

    if not payment_response.data:
        return {
            "message": "Payment record not found"
        }

    payment = payment_response.data[0]

    # Test payment
    supabase.table("payments").update({
        "payment_status": "SUCCESS",
        "transaction_id": f"TEST_TXN_{order_id}"
    }).eq("id", payment["id"]).execute()

    # Update order payment status
    supabase.table("orders").update({
        "payment_status": "SUCCESS"
    }).eq("id", order_id).execute()

    return {
        "message": "Payment successful",
        "order_id": order_id,
        "payment_status": "SUCCESS",
        "transaction_id": f"TEST_TXN_{order_id}"
    }

@app.post("/inventory/reduce/{order_id}")
def reduce_inventory(order_id: int):

    # Get order items
    order_items_response = (
        supabase
        .table("order_items")
        .select("*")
        .eq("order_id", order_id)
        .execute()
    )

    if not order_items_response.data:
        return {
            "message": "No items found for this order"
        }

    updated_items = []

    # Process every item in the order
    for item in order_items_response.data:

        food_item_id = item["food_item_id"]
        ordered_quantity = item["quantity"]

        # Find inventory
        inventory_response = (
            supabase
            .table("inventory")
            .select("*")
            .eq("food_item_id", food_item_id)
            .execute()
        )

        if not inventory_response.data:
            return {
                "message": f"Inventory not found for food item {food_item_id}"
            }

        inventory = inventory_response.data[0]
        current_quantity = inventory["quantity"]

        # Check stock
        if current_quantity < ordered_quantity:
            return {
                "message": f"Not enough stock for food item {food_item_id}",
                "available": current_quantity,
                "requested": ordered_quantity
            }

        new_quantity = current_quantity - ordered_quantity

        # Update inventory
        supabase.table("inventory").update({
            "quantity": new_quantity
        }).eq("id", inventory["id"]).execute()

        updated_items.append({
            "food_item_id": food_item_id,
            "old_quantity": current_quantity,
            "ordered_quantity": ordered_quantity,
            "new_quantity": new_quantity
        })

    return {
        "message": "Inventory updated successfully",
        "order_id": order_id,
        "items": updated_items
    }

@app.get("/orders")
def get_all_orders():

    response = (
        supabase
        .table("orders")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data

@app.get("/orders/{order_id}")
def get_order(order_id: int):

    response = (
        supabase
        .table("orders")
        .select("*")
        .eq("id", order_id)
        .execute()
    )

    if not response.data:
        return {
            "message": "Order not found"
        }

    return response.data[0]

@app.put("/admin/orders/{order_id}/status")
def update_order_status(order_id: int, status: str):

    allowed_statuses = [
        "PLACED",
        "CONFIRMED",
        "PREPARING",
        "READY",
        "COMPLETED",
        "CANCELLED"
    ]

    status = status.upper()

    if status not in allowed_statuses:
        return {
            "message": "Invalid order status",
            "allowed_statuses": allowed_statuses
        }

    response = (
        supabase
        .table("orders")
        .update({
            "order_status": status
        })
        .eq("id", order_id)
        .execute()
    )

    if not response.data:
        return {
            "message": "Order not found"
        }

    return {
        "message": "Order status updated",
        "order_id": order_id,
        "order_status": status
    }

@app.put("/admin/orders/{order_id}/status")
def update_order_status(order_id: int, status: str):

    allowed_statuses = [
        "PLACED",
        "CONFIRMED",
        "PREPARING",
        "READY",
        "COMPLETED",
        "CANCELLED"
    ]

    status = status.upper()

    if status not in allowed_statuses:
        return {
            "message": "Invalid order status",
            "allowed_statuses": allowed_statuses
        }

    # Get order first
    order_response = (
        supabase
        .table("orders")
        .select("*")
        .eq("id", order_id)
        .execute()
    )

    if not order_response.data:
        return {
            "message": "Order not found"
        }

    order = order_response.data[0]

    # Update order status
    update_response = (
        supabase
        .table("orders")
        .update({
            "order_status": status
        })
        .eq("id", order_id)
        .execute()
    )

    # Create notification
    message = f"Your order #{order_id} status is now {status}"

    supabase.table("notifications").insert({
        "user_id": order["user_id"],
        "order_id": order_id,
        "message": message,
        "is_read": False
    }).execute()

    return {
        "message": "Order status updated",
        "order_id": order_id,
        "order_status": status,
        "notification": message
    }

@app.get("/notifications/{user_id}")
def get_notifications(user_id: str):

    response = (
        supabase
        .table("notifications")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data

@app.post("/feedback/{user_id}/{order_id}")
def add_feedback(
    user_id: str,
    order_id: int,
    rating: int,
    comment: str = ""
):

    # Check rating
    if rating < 1 or rating > 5:
        return {
            "message": "Rating must be between 1 and 5"
        }

    # Check whether order exists
    order_response = (
        supabase
        .table("orders")
        .select("*")
        .eq("id", order_id)
        .execute()
    )

    if not order_response.data:
        return {
            "message": "Order not found"
        }

    order = order_response.data[0]

    # Check whether order belongs to user
    if order["user_id"] != user_id:
        return {
            "message": "This order does not belong to this user"
        }

    # Check order is completed
    if order["order_status"] != "COMPLETED":
        return {
            "message": "Feedback can be given only after order is completed"
        }

    # Check if feedback already exists
    existing_feedback = (
        supabase
        .table("feedback")
        .select("*")
        .eq("order_id", order_id)
        .execute()
    )

    if existing_feedback.data:
        return {
            "message": "Feedback already submitted"
        }

    # Insert feedback
    response = (
        supabase
        .table("feedback")
        .insert({
            "user_id": user_id,
            "order_id": order_id,
            "rating": rating,
            "comment": comment
        })
        .execute()
    )

    return {
        "message": "Feedback submitted successfully",
        "feedback": response.data
    }

@app.get("/admin/analytics/sales")
def sales_report():

    # Get successful payments
    response = (
        supabase
        .table("payments")
        .select("*")
        .eq("payment_status", "SUCCESS")
        .execute()
    )

    payments = response.data

    total_sales = 0

    for payment in payments:
        total_sales += float(payment["amount"])

    return {
        "total_transactions": len(payments),
        "total_sales": total_sales
    }

@app.get("/admin/analytics/orders")
def orders_report():

    response = (
        supabase
        .table("orders")
        .select("*")
        .execute()
    )

    orders = response.data

    status_count = {
        "PLACED": 0,
        "CONFIRMED": 0,
        "PREPARING": 0,
        "READY": 0,
        "COMPLETED": 0,
        "CANCELLED": 0
    }

    for order in orders:
        status = order["order_status"]

        if status in status_count:
            status_count[status] += 1

    return {
        "total_orders": len(orders),
        "orders_by_status": status_count
    }

@app.get("/admin/analytics/inventory")
def inventory_report():

    response = (
        supabase
        .table("inventory")
        .select("*, food_items(name)")
        .execute()
    )

    return response.data

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.get_unverified_claims(token)

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )

        return user_id

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    
@app.get("/my-orders/{user_id}")
def get_my_orders(user_id: str):

    response = (
        supabase
        .table("orders")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data

@app.get("/orders/{order_id}/details")
def get_order_details(order_id: int):

    # Get order
    order_response = (
        supabase
        .table("orders")
        .select("*")
        .eq("id", order_id)
        .execute()
    )

    if not order_response.data:
        return {
            "message": "Order not found"
        }

    order = order_response.data[0]

    # Get items in the order
    items_response = (
        supabase
        .table("order_items")
        .select("*, food_items(name, image_url)")
        .eq("order_id", order_id)
        .execute()
    )

    return {
        "order": order,
        "items": items_response.data
    }

@app.get("/profile/{user_id}")
def get_profile(user_id: str):

    response = (
        supabase
        .table("profiles")
        .select("*")
        .eq("id", user_id)
        .execute()
    )

    if not response.data:
        return {
            "message": "Profile not found"
        }

    return response.data[0]

@app.put("/profile/{user_id}")
def update_profile(
    user_id: str,
    name: str | None = None,
    phone: str | None = None
):

    update_data = {}

    if name is not None:
        update_data["name"] = name

    if phone is not None:
        update_data["phone"] = phone

    if not update_data:
        return {
            "message": "No changes provided"
        }

    response = (
        supabase
        .table("profiles")
        .update(update_data)
        .eq("id", user_id)
        .execute()
    )

    if not response.data:
        return {
            "message": "Profile not found"
        }

    return {
        "message": "Profile updated successfully",
        "profile": response.data[0]
    }

def get_current_admin(
    user_id: str = Depends(get_current_user)
):
    response = (
        supabase
        .table("profiles")
        .select("role")
        .eq("id", user_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    role = response.data[0]["role"]

    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return user_id

@app.get("/auth/me")
def get_me(user_id: str = Depends(get_current_user)):
    return {
        "message": "Authentication successful",
        "user_id": user_id
    }
@app.get("/admin/dashboard")
def admin_dashboard():

    # Get all orders
    orders_response = (
        supabase
        .table("orders")
        .select("*")
        .execute()
    )

    orders = orders_response.data

    # Count active orders
    active_orders = 0

    for order in orders:
        if order["order_status"] in [
            "PLACED",
            "CONFIRMED",
            "PREPARING",
            "READY"
        ]:
            active_orders += 1

    # Get successful payments
    payments_response = (
        supabase
        .table("payments")
        .select("*")
        .eq("payment_status", "SUCCESS")
        .execute()
    )

    payments = payments_response.data

    total_sales = 0

    for payment in payments:
        total_sales += float(payment["amount"])

    # Get inventory
    inventory_response = (
        supabase
        .table("inventory")
        .select("*, food_items(name)")
        .execute()
    )

    inventory = inventory_response.data

    # Find low-stock items
    low_stock_items = []

    for item in inventory:
        if item["quantity"] <= 5:
            low_stock_items.append(item)

    return {
        "total_orders": len(orders),
        "active_orders": active_orders,
        "total_sales": total_sales,
        "low_stock_items": low_stock_items
    }

@app.get("/admin/dashboard")
def admin_dashboard():
    return {
        "message": "Admin dashboard API is working"
    }

@app.get("/admin/dashboard")
def admin_dashboard():
    return {
        "message": "Admin dashboard API is working"
    }
@app.put("/orders/{order_id}/cancel")
def cancel_order(order_id: int, user_id: str):

    order_response = (
        supabase
        .table("orders")
        .select("*")
        .eq("id", order_id)
        .execute()
    )

    if not order_response.data:
        return {
            "message": "Order not found"
        }

    order = order_response.data[0]

    if order["user_id"] != user_id:
        return {
            "message": "This order does not belong to this user"
        }

    if order["order_status"] != "PLACED":
        return {
            "message": "Order cannot be cancelled now"
        }

    response = (
        supabase
        .table("orders")
        .update({
            "order_status": "CANCELLED"
        })
        .eq("id", order_id)
        .execute()
    )

    return {
        "message": "Order cancelled successfully",
        "order_id": order_id,
        "order_status": "CANCELLED"
    }

@app.post("/orders/{order_id}/cancel")
def cancel_order_with_notification(order_id: int, user_id: str):

    order_response = (
        supabase
        .table("orders")
        .select("*")
        .eq("id", order_id)
        .execute()
    )

    if not order_response.data:
        return {
            "message": "Order not found"
        }

    order = order_response.data[0]

    if order["user_id"] != user_id:
        return {
            "message": "This order does not belong to this user"
        }

    if order["order_status"] != "PLACED":
        return {
            "message": "Order cannot be cancelled now"
        }

    supabase.table("orders").update({
        "order_status": "CANCELLED"
    }).eq("id", order_id).execute()

    message = f"Your order #{order_id} has been cancelled"

    supabase.table("notifications").insert({
        "user_id": user_id,
        "order_id": order_id,
        "message": message,
        "is_read": False
    }).execute()

    return {
        "message": "Order cancelled successfully",
        "order_id": order_id,
        "order_status": "CANCELLED",
        "notification": message
    }

@app.put("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int):

    response = (
        supabase
        .table("notifications")
        .update({
            "is_read": True
        })
        .eq("id", notification_id)
        .execute()
    )

    if not response.data:
        return {
            "message": "Notification not found"
        }

    return {
        "message": "Notification marked as read",
        "notification": response.data[0]
    }

@app.get("/notifications/{user_id}/unread")
def get_unread_notifications(user_id: str):

    response = (
        supabase
        .table("notifications")
        .select("*")
        .eq("user_id", user_id)
        .eq("is_read", False)
        .order("created_at", desc=True)
        .execute()
    )

    return {
        "unread_count": len(response.data),
        "notifications": response.data
    }

@app.get("/feedback/user/{user_id}")
def get_user_feedback(user_id: str):

    response = (
        supabase
        .table("feedback")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data

@app.get("/admin/feedback")
def get_all_feedback():

    response = (
        supabase
        .table("feedback")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    feedback = response.data

    total_feedback = len(feedback)

    total_rating = 0

    for item in feedback:
        total_rating += item["rating"]

    average_rating = 0

    if total_feedback > 0:
        average_rating = round(
            total_rating / total_feedback,
            2
        )

    return {
        "total_feedback": total_feedback,
        "average_rating": average_rating,
        "feedback": feedback
    }

@app.get("/food-items/{food_id}/availability")
def check_food_availability(food_id: int):

    response = (
        supabase
        .table("food_items")
        .select("id, name, available, stock_quantity")
        .eq("id", food_id)
        .execute()
    )

    if not response.data:
        return {
            "message": "Food item not found"
        }

    food = response.data[0]

    return {
        "food_item_id": food["id"],
        "name": food["name"],
        "available": food["available"],
        "stock_quantity": food["stock_quantity"]
    }

class CartItemRequest(BaseModel):
    food_item_id: int
    quantity: int = 1


class PaymentRequest(BaseModel):
    payment_method: str


class FeedbackRequest(BaseModel):
    rating: int
    comment: str = ""


class ProfileUpdateRequest(BaseModel):
    name: str | None = None
    phone: str | None = None

