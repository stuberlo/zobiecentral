from typing import Annotated, Dict
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select, Column, JSON
from collections import Counter
from pydantic import ValidationError, BaseModel

""" DATABASE SETUP """

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


""" MODELS """

""" the sqlmodels are working as both validation through pydantic and as models for the sqllite database"""


class SurvivorBase(SQLModel):
    id: int | None = Field(primary_key=True)
    icon: str = Field(default="man-zombie.png", index=True)


class Location(BaseModel):
    lat: float
    lon: float


class Survivor(SurvivorBase, table=True):
    name: str = Field(index=True, min_length=1)
    age: int = Field(index=True)
    gender: str = Field(index=True)
    last_location: Location = Field(sa_column=Column(JSON))
    inventory: Dict[str, int] = Field(default={}, sa_column=Column(JSON))
    infected_flag_count: int = Field(default=0, index=True)
    infected: bool = Field(default=False, index=True)


class TradeInfo(BaseModel):
    s1_id: int
    s2_id: int
    s1_trades: dict[str, int]
    s2_trades: dict[str, int]


""" Endpoints """


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/survivors/")
def register_survivor(survivor: Survivor, session: SessionDep) -> Survivor:
    try:
        Survivor.model_validate(survivor)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    survivor.inventory = {k: int(v) for k, v in survivor.inventory.items()}
    if "female" in survivor.gender:
        survivor.icon = "woman-pouting.png"
    else:
        survivor.icon = "man-pouting.png"
    session.add(survivor)
    session.commit()
    session.refresh(survivor)

    return survivor


@app.get("/survivors/")
def retrieve_survivors(
    session: SessionDep,
) -> list[Survivor]:
    return session.exec(select(Survivor)).all()


@app.get("/survivors/{survivor_id}")
def retrieve_survivor(
    survivor_id: int,
    session: SessionDep,
) -> Survivor:
    if survivor := session.get(Survivor, survivor_id):
        return survivor
    raise HTTPException(
        status_code=400, detail=f"Survivor with id {survivor_id} not found in database"
    )


@app.post("/update_location/{survivor_id}")
def update_location(
    location: Location,
    survivor_id: int,
    session: SessionDep,
) -> Survivor:
    survivor = session.get(Survivor, survivor_id)
    survivor.last_location = dict(location)
    session.commit()
    session.refresh(survivor)
    return survivor


@app.get("/flag_as_infected/{survivor_id}")
def flag_as_infected(
    survivor_id: int,
    session: SessionDep,
) -> Survivor:
    survivor = session.get(Survivor, survivor_id)
    survivor.infected_flag_count += 1
    if survivor.infected_flag_count >= 3:
        survivor.infected = True
        if "female" in survivor.gender:
            survivor.icon = "woman-zombie.png"
        else:
            survivor.icon = "man-zombie.png"
    session.commit()
    session.refresh(survivor)
    return survivor


@app.get("/display_inventory/{survivor_id}")
def display_inventory(
    survivor_id: int,
    session: SessionDep,
) -> dict:
    return session.get(Survivor, survivor_id).inventory


def update_inventories(
    from_survivor: Survivor = None,
    trade_items: dict = {},
    from_inv: dict = {},
    to_inv: dict = (),
):
    # use of counters to default empty key to 0
    from_inv = Counter(from_inv)
    to_inv = Counter(to_inv)
    for item, amount in trade_items.items():
        if amount > from_inv[item]:
            raise HTTPException(
                status_code=400,
                detail=f"Survivor {from_survivor.name} doesn't have enough ({amount}) {item} to trade! (has {from_inv[item]})",
            )
        else:
            from_inv[item] -= amount
            if from_inv[item] == 0:
                from_inv.pop(item)
            to_inv[item] += amount
    return dict(from_inv), dict(to_inv)


@app.post("/trade_items/")
def trade_items(
    trade_info: TradeInfo,
    session: SessionDep,
) -> dict:

    # hard coded price table
    item_table = {
        "water": 4,
        "food": 3,
        "medication": 2,
        "ammunition": 1,
    }

    s1 = session.get(Survivor, trade_info.s1_id)
    s2 = session.get(Survivor, trade_info.s2_id)

    # check if any are infected, is so: no trade
    if s1.infected or s2.infected:
        raise HTTPException(
            status_code=400,
            detail="No trade made since at least one of the survivors is infected!",
        )

    # check if total value matches exactly, otherwise: no trade
    s1_trades = trade_info.s1_trades
    s2_trades = trade_info.s2_trades
    total_value = lambda trade_goods: sum(
        item_table.get(item, 0) * amount for item, amount in trade_goods.items()
    )  # if item not in price table, treat it as zero value
    if total_value(s1_trades) != total_value(s2_trades):
        raise HTTPException(
            status_code=400, detail="Trading value must be equal for both parts!"
        )

    # survivor 1 trades his item with survivor 2
    s1_inv, s2_inv = update_inventories(
        from_survivor=s1,
        trade_items=s1_trades,
        from_inv=s1.inventory,
        to_inv=s2.inventory,
    )
    # survivor 2 trades his item with survivor 1
    s2_inv, s1_inv = update_inventories(
        from_survivor=s2, trade_items=s2_trades, from_inv=s2_inv, to_inv=s1_inv
    )

    # hack due to bug in sqlmodel, must commit twice to update data
    s1.sqlmodel_update({})
    s2.sqlmodel_update({})
    session.add(s1)
    session.add(s2)
    session.commit()

    s1.sqlmodel_update({"inventory": s1_inv})
    s2.sqlmodel_update({"inventory": s2_inv})
    session.add(s1)
    session.add(s2)
    session.commit()
    return {"trade_outcome": "success!"}
