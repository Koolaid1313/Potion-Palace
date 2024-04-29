from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    # Updates the tables
    with db.engine.begin() as connection:
        for potion in potions_delivered:
            # Updates the number of mls in table
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO inventory_ledgers 
                (gold, red_ml, green_ml, blue_ml, dark_ml) 
                VALUES 
                (0, :red_ml, :green_ml, :blue_ml, :dark_ml)
                """),
                {"red_ml": -potion.potion_type[0] * potion.quantity, "green_ml": -potion.potion_type[1] * potion.quantity, 
                  "blue_ml": -potion.potion_type[2] * potion.quantity,"dark_ml": -potion.potion_type[3] * potion.quantity})
            
            # Updates the number of potions in table
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO potion_ledgers 
                (sku, change) 
                SELECT sku, :quantity
                FROM potions
                WHERE potions.type = :potion_type
                """),
                {"quantity": potion.quantity, "potion_type": potion.potion_type})
        
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    with db.engine.begin() as connection:
        mls_result = connection.execute(sqlalchemy.text(
            """
            SELECT 
            SUM(red_ml) AS red_ml, 
            SUM(green_ml) AS green_ml, 
            SUM(blue_ml) AS blue_ml, 
            SUM(dark_ml) AS dark_ml
            FROM inventory_ledgers
            """)).one()
        
        potions = connection.execute(sqlalchemy.text(
            """
            SELECT 
            sku, name, type, price
            FROM potions
            ORDER BY price DESC
            """)).all()
        
    bottle_plan = []
    mls = [mls_result.red_ml, mls_result.green_ml, mls_result.blue_ml, mls_result.dark_ml]
    
    # Bottle all mls into potions
    for potion in potions:

        # High to help with first comparison below
        num_potions = 10000

        # Determine number of potions that could be brewed
        for i in range(4):
            if potion.type[i] > 0:
                temp_count = mls[i] // potion.type[i]
                if temp_count < num_potions:
                    num_potions = temp_count

        if num_potions != 0:
            # Update mls in list
            for i in range(4):
                if potion.type[i] > 0:
                    mls[i] -= num_potions * potion.type[i]

            # Add to bottle plan
            bottle_plan.append({
                "potion_type": potion.type,
                "quantity": num_potions
            })
 
    return bottle_plan

if __name__ == "__main__":
    print(get_bottle_plan())