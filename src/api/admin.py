from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """
            DELETE FROM cart_items;
            DELETE FROM carts;
            DELETE FROM potion_ledgers;
            DELETE FROM inventory_ledgers;
            INSERT INTO inventory_ledgers
            (gold) VALUES (100);
            DELETE FROM capacity;
            INSERT INTO capacity
            (ml_capacity, potion_capacity)
            VALUES (10000, 50);
            """))

    return "OK"

