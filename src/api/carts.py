from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """
    results = []
    query = """
        SELECT ci.id, ci.item_sku, c.customer_name, (p.price * ci.quantity) AS line_item_total, c.created_at AS timestamp
        FROM carts AS c
        LEFT JOIN cart_items AS ci ON c.cart_id = ci.cart_id
        LEFT JOIN potions AS p ON p.sku = ci.item_sku
        """
    
    # Filtering
    if customer_name:
        query += f" WHERE LOWER(customer_name) LIKE LOWER('{customer_name}')"
        if potion_sku:
            query += f" AND LOWER(item_sku) LIKE LOWER('{potion_sku}')"
    elif potion_sku:
        query += f" WHERE LOWER(item_sku) LIKE LOWER('{potion_sku}')"

    # Sorting
    query += f" ORDER BY {sort_col.value} {sort_order.value}"
    
    # Pagination
    if search_page:
        query += f" OFFSET {int(search_page)*5}"

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(query)).fetchall()

        for row in result:
            results.append({
                "line_item_id": row[0],
                "item_sku": row[1],
                "customer_name": row[2],
                "line_item_total": row[3],
                "timestamp": row[4].isoformat() if row[4] else None,
            })

    # Convert search_page to int
    search_page_int = int(search_page) if search_page.isdigit() else 0
    
    return {
        "previous": str(search_page_int - 1) if search_page_int > 0 else "",
        "next": str(search_page_int + 1) if len(results) > 5 else "",
        "results": results[:5]
    }

class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            INSERT INTO carts (customer_name, character_class, level)
            VALUES (:name, :class, :level)
            RETURNING cart_id
            """), 
            [{"name": new_cart.customer_name, "class": new_cart.character_class, 
              "level": new_cart.level}]).one()
        
    return {"cart_id": result[0]}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """
            INSERT INTO cart_items (cart_id, item_sku, quantity)
            VALUES (:id, :sku, :quantity)
            """), 
            [{"id": cart_id, "sku": item_sku, "quantity": cart_item.quantity}])
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    print(cart_checkout)

    with db.engine.begin() as connection:
        # Get a list of all items in cart
        items = connection.execute(sqlalchemy.text(
            """
            SELECT * 
            FROM cart_items
            WHERE cart_id = :id
            """), 
            [{"id": cart_id}]).all()
        
        # Get the sum of all the prices and quantities
        gold = 0
        quantity = 0
        for item in items:
            result = connection.execute(sqlalchemy.text(
                """
                SELECT price 
                FROM potions
                WHERE sku = :sku
                """), [{"sku": item.item_sku}]).one()
            gold += result.price * item.quantity
            quantity += item.quantity

            # Update the inventory
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO potion_ledgers
                (sku, change)
                VALUES
                (:sku, :quantity)
                """), [{"sku": item.item_sku, "quantity": -item.quantity}])
        
        # Update the gold
        connection.execute(sqlalchemy.text(
                """
                INSERT INTO inventory_ledgers
                (gold) VALUES (:gold)
                """), [{"gold": gold}])
        
    return {"total_potions_bought": quantity, "total_gold_paid": gold}
