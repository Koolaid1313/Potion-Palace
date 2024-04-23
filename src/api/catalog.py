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
            SELECT *
            FROM potions
            """)).all()

    catalog = []

    for potion in result:
        if potion.quantity > 0:
            catalog.append({
                    "sku": potion.sku,
                    "name": potion.name,
                    "quantity": potion.quantity,
                    "price": potion.price,
                    "potion_type": potion.type,
                })
        
    return catalog
