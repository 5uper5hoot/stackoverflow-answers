from dataclasses import dataclass


@dataclass(frozen=True)
class OrderLine:
    id: str
    sku: str
    quantity: int
