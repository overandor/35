from fastapi import FastAPI
from pydantic import BaseModel
from spreadish.exchange import get_exchange

class Position(BaseModel):
    symbol: str
    side: str
    quantity: float
    price: float
    dry_run: bool = True

app = FastAPI()
exchange = get_exchange()

@app.post("/positions")
def create_position(position: Position):
    """
    Creates a new perpetual futures position.
    """
    if position.dry_run:
        return {"message": f"Dry run: Created a {position.side} position for {position.quantity} {position.symbol} at {position.price}."}
    else:
        try:
            order = exchange.create_order(position.symbol, 'limit', position.side, position.quantity, position.price)
            return {"message": f"Live: Created a {position.side} position for {position.quantity} {position.symbol} at {position.price}.", "order": order}
        except Exception as e:
            return {"message": f"Error creating order: {e}"}
