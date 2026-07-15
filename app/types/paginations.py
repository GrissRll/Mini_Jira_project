from dataclasses import dataclass


@dataclass(slots=True)
class Pagination:
    page_num: int = 1
    page_size: int = 10
