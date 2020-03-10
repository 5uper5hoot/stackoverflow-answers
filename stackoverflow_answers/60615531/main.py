from sqlalchemy import Column, Integer, String
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


# this produces the set of common attributes that each class should have
def attribute_factory():
    return dict(
        id=Column(Integer, primary_key=True),
        name=Column(String, nullable=False),
        state=Column(String, nullable=False),
        CLASS_VAR=12345678,
    )


states = ["CA", "TX", "NY"]


# here we map the state abbreviation to the generated model, notice the templated
# class and table names
model_map = {
    state: type(
        f"Employee_{state}",
        (Base,),
        dict(**attribute_factory(), __tablename__=f"Employee_{state}"),
    )
    for state in states
}


engine = create_engine("sqlite:///", echo=True)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)


if __name__ == "__main__":
    # inserts work
    s = Session()
    for state, model in model_map.items():
        s.add(model(name="something", state=state))
    s.commit()
    s.close()

    # queries work
    s = Session()
    for state, model in model_map.items():
        inst = s.query(model).first()
        print(inst.state, inst.CLASS_VAR)
