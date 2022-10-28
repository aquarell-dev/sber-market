from dataclasses import dataclass
from typing import List, Any

from dataclasses_json import dataclass_json


@dataclass
class Urls:
    retailer_url: str
    stores_url: str
    categories_url: str

    def get_stores_url(self, city_id: str, retailer_id: str) -> str:
        return self.stores_url % (city_id, retailer_id)

    def get_categories_url(self, sid: int) -> str:
        return self.categories_url % str(sid)


@dataclass_json
@dataclass
class Category:
    title: str
    url: str
    children: List['Category'] = None


@dataclass_json
@dataclass
class Store:
    sid: int
    title: str
    retailer_id: str
    address: str
    url: str
    categories: List[Category] = None
