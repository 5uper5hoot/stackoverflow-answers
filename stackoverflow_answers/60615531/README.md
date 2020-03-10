Creating dynamic classes in SQLAlchemy
======================================
https://stackoverflow.com/questions/60615531/creating-dynamic-classes-in-sqlalchemy

We have 1 table with a large amount of data and DBA's partitioned it based on a particular parameter. This means I ended up with `Employee_TX, Employee_NY` kind of table names. Earlier the `models.py` was simple as in --

    class Employee(Base):
        __tablename__ = 'Employee'
        name = Column...
        state = Column...

Now, I don't want to create 50 new classes for the newly partitioned tables as anyways my columns are the same.

Is there a pattern where I can create a single class and then use it in query dynamically? `session.query(<Tablename>).filter().all()`

Maybe some kind of Factory pattern or something is what I'm looking for.

So far I've tried by running a loop as

    for state in ['CA', 'TX', 'NY']:
        class Employee(Base):
            __qualname__ = __tablename__ = 'Employee_{}'.format(state)
            name = Column...
            state = Column...

but this doesn't work and I get a warning as - `SAWarning: This declarative base already contains a class with the same class name and module name as app_models.employee, and will be replaced in the string-lookup table.`

Also it can't find the generated class when I do `from app_models import Employee_TX`

This is a flask app with PostgreSQL as a backend and sqlalchemy is used as an ORM