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
                UPDATE global_inventory SET 
                red_ml = red_ml - :red_ml_used,
                green_ml = green_ml - :green_ml_used,
                blue_ml = blue_ml - :blue_ml_used,
                dark_ml = dark_ml - :dark_ml_used
                """),
                {"red_ml_used": potion.potion_type[0] * potion.quantity, "green_ml_used": potion.potion_type[1] * potion.quantity, 
                  "blue_ml_used": potion.potion_type[2] * potion.quantity,"dark_ml_used": potion.potion_type[3] * potion.quantity})
            
            # Updates the number of potions in table
            connection.execute(sqlalchemy.text(
                """
                UPDATE potions SET 
                quantity = quantity + :quantity
                WHERE type = :potion_type
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
            red_ml,
            green_ml,
            blue_ml,
            dark_ml
            FROM global_inventory
            """)).one()
        potions = connection.execute(sqlalchemy.text(
            """
            SELECT *
            FROM potions
            """)).all()
        
    #Bottle all mls into potions
    for potion in potions:
        brewable = True
        mls = [mls_result.red_ml, mls_result.green_ml, mls_result.blue_ml, mls_result.dark_ml]

        # Determine if brewable
        for i in range(4):
            if potion.type[i] > mls[i]:
                brewable = False
        
        if brewable:
            # High to help with first comparison below
            num_potions = 1000

            # Determine number of potions that can be brewed
            for i in range(4):
                if potion.type[i] != 0:
                    temp_count = 0
                    while potion.type[i] <= mls[i]:
                        temp_count += 1
                        mls[i] -= potion.type[i]

                    if temp_count < num_potions:
                        num_potions = temp_count

            # Returns the correct number of potions
            return [
                    {
                        "potion_type": potion.type,
                        "quantity": num_potions
                    }
                ]
 
    return []

if __name__ == "__main__":
    print(get_bottle_plan())