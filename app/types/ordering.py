from dataclasses import dataclass
from app.repositories.tasks import OrderedColumns, TypeOfOrdering


@dataclass(slots=True)
class Ordering:
    columns: tuple[OrderedColumns, ...]
    direction: TypeOfOrdering = "asc"
