from pydantic import BaseModel


class ChainItem(BaseModel):
    name: str
    id: int
    rpc: str
    explorer: str
    checkin_contract: str

    def __hash__(self):
        return hash((self.name, self.id, self.rpc, self.explorer, self.checkin_contract))
