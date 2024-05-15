from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        inventory = connection.execute(sqlalchemy.text(
            """
            SELECT SUM(gold) AS gold,
            SUM(red_ml + green_ml + blue_ml + dark_ml) AS total_ml
            FROM inventory_ledgers
            """)).one()
        
        # Sum to extract potions quantity
        potions = connection.execute(sqlalchemy.text(
            """
            SELECT COALESCE(SUM(change), 0) AS sum
            FROM potion_ledgers
            """)).one()

    return {"number_of_potions": potions.sum, 
            "ml_in_barrels": inventory.total_ml, 
            "gold": inventory.gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    # temp
    return {
        "potion_capacity": 0,
        "ml_capacity": 9
    }

    with db.engine.begin() as connection:
        # Get gold and mls
        inventory = connection.execute(sqlalchemy.text(
            """
            SELECT SUM(gold) AS gold,
            SUM(red_ml + green_ml + blue_ml + dark_ml) AS total_ml
            FROM inventory_ledgers
            """)).one()
        
        # Sum to extract potions quantity
        potions = connection.execute(sqlalchemy.text(
            """
            SELECT COALESCE(SUM(change), 0) AS sum
            FROM potion_ledgers
            """)).one()
        
        # Get the current capacity
        capacity = connection.execute(sqlalchemy.text(
            """
            SELECT ml_capacity AS mls, 
            potion_capacity AS potions
            FROM capacity
            """)).one()

    if inventory.gold >= 2500:
        if potions.sum >= capacity.potions - 10:
            return {
                "potion_capacity": 1,
                "ml_capacity": 0
            }
        elif inventory.total_ml >= capacity.mls - 4000:
            return {
                "potion_capacity": 0,
                "ml_capacity": 1
            }

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
    }      

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    with db.engine.begin() as connection:
        # Updates the capacity
        connection.execute(sqlalchemy.text(
            """
            UPDATE capacity SET
            ml_capacity = ml_capacity + :mls,
            potion_capacity = potion_capacity + :potions
            """), 
            [{"mls": capacity_purchase.ml_capacity * 10000, 
              "potions": capacity_purchase.potion_capacity * 50}])
        
        # Adds a ledger for gold
        connection.execute(sqlalchemy.text(
            """
            INSERT INTO inventory_ledgers
            (gold)
            VALUES
            (:gold)
            """), 
            [{"gold": -(capacity_purchase.ml_capacity + capacity_purchase.potion_capacity) * 1000}])
        
    return "OK"
