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
        result = connection.execute(sqlalchemy.text(
            """
            SELECT 
            red_potions, 
            green_potions,
            blue_potions,
            dark_potions
            FROM global_inventory
            """)).one()

    return [
            {
                "sku": "RED_POTION",
                "name": "red potion",
                "quantity": result.red_potions,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            },
            {
                "sku": "GREEN_POTION",
                "name": "green potion",
                "quantity": result.green_potions,
                "price": 50,
                "potion_type": [0, 100, 0, 0],
            },
            {
                "sku": "BLUE_POTION",
                "name": "blue potion",
                "quantity": result.blue_potions,
                "price": 50,
                "potion_type": [0, 0, 100, 0],
            },
            {
                "sku": "DARK_POTION",
                "name": "dark potion",
                "quantity": result.dark_potions,
                "price": 100,
                "potion_type": [0, 0, 0, 100],
            }
        ]
