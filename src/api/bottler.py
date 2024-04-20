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
    
    red_potions = 0
    green_potions = 0
    blue_potions= 0
    dark_potions = 0

    #gets the correct number of potions to add
    for potion in potions_delivered:
        if potion.potion_type == [100, 0, 0, 0]:
            red_potions += potion.quantity
        elif potion.potion_type == [0, 100, 0, 0]:
            green_potions += potion.quantity
        elif potion.potion_type == [0, 0, 100, 0]:
            blue_potions += potion.quantity
        elif potion.potion_type == [0, 0, 0, 100]:
            dark_potions += potion.quantity
        else:
            raise Exception("Invalid potion type")
        
    # Updates the number of potions in table
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """
            UPDATE global_inventory SET 
            red_potions = red_potions + :red_potions,
            green_potions = green_potions + :green_potions,
            blue_potions = blue_potions + :blue_potions,
            dark_potions = dark_potions + :dark_potions
            """),
            [{"red_potions": red_potions,"green_potions": green_potions,"blue_potions": blue_potions,"dark_potions": dark_potions}])

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
        result = connection.execute(sqlalchemy.text(
            """
            SELECT 
            red_ml,
            green_ml,
            blue_ml,
            dark_ml
            FROM global_inventory
            """)).one()
        
    potion_types = [[100, 0, 0, 0], [0, 100, 0, 0], [0, 0, 100, 0], [0, 0, 0, 100]]
    #Bottle all mls into potions
    for mls , potion_type in zip([result.red_ml, result.green_ml, result.blue_ml, result.dark_ml], potion_types):
        if mls > 0:
            num_potions = 0

            # Run for every 100 ml until empty
            while mls >= 100:
                num_potions += 1
                mls -= 100

            # Returns the correct number of potions
            return [
                    {
                        "potion_type": potion_type,
                        "quantity": num_potions
                    }
                ]
 
    return []

if __name__ == "__main__":
    print(get_bottle_plan())