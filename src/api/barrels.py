from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    with db.engine.begin() as connection:
        num_green = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).fetchone()[0]
        num_blue = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).fetchone()[0]
        num_red = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).fetchone()[0]

    print(wholesale_catalog)

    # If there are less than 10 green potions purchase a small green barrel
    if num_green < 5:
        return [
            {
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1,
            }
        ]
    elif num_blue < 5:
        return [
            {
                "sku": "SMALL_BLUE_BARREL",
                "quantity": 1,
            }
        ]
    elif num_red < 5:
        return [
            {
                "sku": "SMALL_RED_BARREL",
                "quantity": 1,
            }
        ]
    else:
        return []

