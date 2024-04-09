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

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Bottle all barrels into green potions.
    with db.engine.begin() as connection:
        mls = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))

    if mls > 0:
        num_potions = 0

        # Run for every 100 ml until empty
        while mls > 0:
            num_potions += 1
            mls -= 100

        # Get the current number of green potions
        with db.engine.begin() as connection:
            curr_green = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))

        # Updates the number of mls and potions in table
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = 0"))
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_potions = {num_potions + curr_green}"))

        # Returns the correct number of green potions
        return [
                {
                    "potion_type": [0, 100, 0, 0],
                    "quantity": num_potions,
                }
            ]
    else:
        return []

if __name__ == "__main__":
    print(get_bottle_plan())