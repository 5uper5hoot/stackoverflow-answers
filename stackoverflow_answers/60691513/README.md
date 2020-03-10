SQLAlchemy: How to delete and flush instead of commit?
======================================================
https://stackoverflow.com/questions/60691513/sqlalchemy-how-to-delete-and-flush-instead-of-commity

I would like to reduce the number of `db.session.commit()` in the code to reduce the over-utilisation of the database. I think it suffices to have only one `commit()` at the end of the request. Hence I'm going through every path and replace the commit() with flush().

But it doesn't seem to work with delete.

    db.session.delete(account.receipt)
    db.session.flush()

Despite flushing `account.receipt` is still present and my unit tests are failing. Is there any other way to achieve this or do I have no other way than to use `commit()` here?

Answer
======

Explicit deletion of an object through the session, such as `db.session.delete(account.receipt)` does not result in the disassociation of the child object from its parent until `commit()` is called on the session. This means that until the commit occurs, expressions such as `if parent.child: ...` will still evaluate truthy after flush and before commit.

Instead of relying on truthyness, we can check the object state in our logic, as once `flush()` has been called, the state of the deleted object changes from `persistent` to `deleted` ([Quicky Intro to Object States][2]):

```py
from sqlalchemy import inspect

if not inspect(parent.child).deleted:
    ...
```
or
```py
if parent.child not in session.deleted:
    ...
```

Where it makes no sense for a child object to exist independent of it's parent, it might instead be better to set the cascade on the parent relationship attribute to include the [`'delete-orphan'`][1] directive. The child object is then automatically deleted from the session once it is disassociated from the parent allowing for immediate truthyness testing of the parent attribute, and the same semantics upon rollback (i.e., child object restored). A child relationship on the parent that includes the `'delete-orphan'` directive might look like this:
```py
child = relationship("Child", uselist=False, cascade="all, delete-orphan")
```
and a delete sequence with truthy test, and no db commit looks like this:

```py
child = Child()
parent.child = child

s.commit()

parent.child = None
s.flush()

if parent.child:  # obviously not executed, we just set to None!
    print("not executed")
print(f"{inspect(child).deleted = }")  # inspect(child).deleted = True

s.rollback()  # child object restored

if parent.child:
    print("executed")
```

Here's a somewhat longish, but fully self contained (py3.8+) script that demonstrates the different states an object passes through, and the truthyness of the parent attribute, using both the explicit session deletion method and the implicit deletion through nulling the parent relationship and setting the 'delete-orphan' cascade:

```py
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
```

[1]: https://docs.sqlalchemy.org/en/13/orm/cascades.html?highlight=delete%20orphan
[2]: https://docs.sqlalchemy.org/en/13/orm/session_state_management.html#quickie-intro-to-object-states