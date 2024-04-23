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
        gold_mls = connection.execute(sqlalchemy.text(
            """
            SELECT 
            gold,
            red_ml,
            green_ml,   
            blue_ml,
            dark_ml,        
            FROM global_inventory
            """)).one()
        potions = connection.execute(sqlalchemy.text(
            """
            SELECT 
            quantity     
            FROM potions
            """)).all()

    return {"number_of_potions": sum(potions), 
            "ml_in_barrels": gold_mls.red_ml + gold_mls.green_ml + gold_mls.blue_ml + gold_mls.dark_ml, 
            "gold": gold_mls.gold}

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
