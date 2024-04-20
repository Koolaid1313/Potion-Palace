from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import random
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
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}\n")

    gold_paid = 0
    red_ml = 0
    green_ml = 0
    blue_ml = 0
    dark_ml = 0

    for barrel in barrels_delivered:
        gold_paid += barrel.price * barrel.quantity
        mls = barrel.ml_per_barrel * barrel.quantity
        if barrel.potion_type == [1,0,0,0]:
            red_ml += mls
        elif barrel.potion_type == [0,1,0,0]:
            green_ml += mls
        elif barrel.potion_type == [0,0,1,0]:
            blue_ml += mls
        elif barrel.potion_type == [0,0,0,1]:
            dark_ml += mls
        else:
            raise Exception("Invalid potion type")
        
    print(f"gold_paid: {gold_paid}, red_ml: {red_ml}, green_ml: {green_ml}, blue_ml: {blue_ml}, dark_ml: {dark_ml}\n")

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE global_inventory SET
                gold = gold - :gold_paid,  
                red_ml = red_ml + :red_ml,
                green_ml = green_ml + :green_ml,
                blue_ml = blue_ml + :blue_ml,
                dark_ml = dark_ml + :dark_ml
                """),
                [{"gold_paid": gold_paid, "red_ml": red_ml,"green_ml": green_ml,"blue_ml": blue_ml,"dark_ml": dark_ml}])

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT gold, 
            red_ml,
            green_ml,
            blue_ml,
            dark_ml
            FROM global_inventory
            """)).one()

    # Define potion types in a dictionary
    potions = {
        "RED": result.red_ml, 
        "GREEN": result.green_ml, 
        "BLUE": result.blue_ml, 
        "DARK": result.dark_ml
    }

    print(potions)

    # Shuffle the potions
    shuffled_potion_names = list(potions.keys())
    random.shuffle(shuffled_potion_names)

    # Iterate over the shuffled potions
    for potion_name in shuffled_potion_names:
        if potions[potion_name] == 0:
            return [
                {
                   "sku": f"SMALL_{potion_name}_BARREL",
                   "quantity": 1,
                }
            ]
        
    return []
