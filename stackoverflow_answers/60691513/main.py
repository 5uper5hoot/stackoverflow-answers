import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

engine = sa.create_engine("sqlite:///", echo=False)

Session = sessionmaker(bind=engine)

Base = declarative_base()


class Parent(Base):
    __tablename__ = "parents"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    child = relationship("Child", uselist=False, cascade="all, delete-orphan")


class Child(Base):
    __tablename__ = "children"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("parents.id"), nullable=True)


def truthy_test(parent: Parent) -> None:
    if parent.child:
        print("parent.child tested Truthy")
    else:
        print("parent.child tested Falsy")


Base.metadata.create_all(engine)

parent = Parent()
child = Child()
parent.child = child

insp_child = sa.inspect(child)

print("***Example 1: explicit session delete***")

print("\nInstantiated Child")
print(f"{insp_child.transient = }")  # insp_child.transient = True

s = Session()
s.add(parent)

print("\nChild added to session.")
print(f"{insp_child.transient = }")  # insp_child.transient = False
print(f"{insp_child.pending = }")  # insp_child.pending = True

s.commit()

print("\nAfter commit")
print(f"{insp_child.pending = }")  # insp_child.pending = False
print(f"{insp_child.persistent = }")  # insp_child.persistent = True
truthy_test(parent)

s.delete(parent.child)
s.flush()

print("\nAfter Child deleted and flush")
print(f"{insp_child.persistent = }")  # insp_child.persistent = False
print(f"{insp_child.deleted = }")  # insp_child.deleted = True
truthy_test(parent)

s.rollback()

print("\nAfter Child deleted and rollback")
print(f"{insp_child.persistent = }")  # insp_child.persistent = False
print(f"{insp_child.deleted = }")  # insp_child.deleted = True
truthy_test(parent)

s.delete(parent.child)
s.commit()

print("\nAfter Child deleted and commit")
print(f"{insp_child.deleted = }")  # insp_child.deleted = False
print(f"{insp_child.detached = }")  # insp_child.detached = True
print(f"{insp_child.was_deleted = }")  # insp_child.was_deleted = True
truthy_test(parent)


print("\n***Example 2: implicit session delete through parent disassociation***")

child2 = Child()
parent.child = child2

s.commit()

parent.child = None  # type:ignore
s.flush()
print("\nParent.child set to None, after flush")
print(f"{sa.inspect(child2).deleted = }, if 'delete-orphan' not set, this is False")
truthy_test(parent)

s.rollback()

print("\nParent.child set to None, after flush, and rollback")
print(f"{sa.inspect(child2).deleted = }, if 'delete-orphan' not set, this is False")
truthy_test(parent)

parent.child = None  # type:ignore
s.commit()
print("\nParent.child set to None, after commit")
print(f"{sa.inspect(child2).detached = }, if 'delete-orphan not set, this is False")
truthy_test(parent)
