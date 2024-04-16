from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    # Get the current number of potions
    with db.engine.begin() as connection:
        num_green = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).fetchone()[0]
        num_blue = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).fetchone()[0]
        num_red = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).fetchone()[0]

    return [
            {
                "sku": "GREEN_POTION",
                "name": "green potion",
                "quantity": num_green,
                "price": 50,
                "potion_type": [0, 100, 0, 0],
            },
            {
                "sku": "BLUE_POTION",
                "name": "blue potion",
                "quantity": num_blue,
                "price": 50,
                "potion_type": [0, 0, 100, 0],
            },
            {
                "sku": "RED_POTION",
                "name": "red potion",
                "quantity": num_red,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]
