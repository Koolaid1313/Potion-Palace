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
            SUM(red_ml) AS red_ml, 
            SUM(green_ml) AS green_ml, 
            SUM(blue_ml) AS blue_ml, 
            SUM(dark_ml) AS dark_ml
            FROM inventory_ledgers
            """)).one()
        
        # Sum to extract potions quantity
        potions = connection.execute(sqlalchemy.text(
            """
            SELECT COALESCE(SUM(change), 0) AS sum
            FROM potion_ledgers
            """)).one()

    return {"number_of_potions": potions.sum, 
            "ml_in_barrels": inventory.red_ml + inventory.green_ml + inventory.blue_ml + inventory.dark_ml, 
            "gold": inventory.gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

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

    return "OK"
