Unable to Instantiate Python Dataclass (Frozen) inside a Pytest function that uses Fixtures
===========================================================================================
https://stackoverflow.com/questions/61419449/unable-to-instantiate-python-dataclass-frozen-inside-a-pytest-function-that-us

I'm following along with Architecture Patterns in Python by Harry Percival and Bob Gregory.

Around chapter three (3) they introduce testing the ORM of SQLAlchemy.

A new test that requires a `session` fixture, it is throwing `AttributeError, FrozenInstanceError` due to `cannot assign to field '_sa_instance_state'`

It may be important to note that other tests do not fail when creating instances of `OrderLine`, but they do fail if I simply include `session` into the test parameter(s).

Anyway I'll get straight into the code.

*conftest.py*
```python
@pytest.fixture
def local_db():
    engine = create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(local_db):
    start_mappers()
    yield sessionmaker(bind=local_db)()
    clear_mappers()
```

*model.py*
```python
@dataclass(frozen=True)
class OrderLine:
    id: str
    sku: str
    quantity: int
```

*test_orm.py*
```python
def test_orderline_mapper_can_load_lines(session):
    session.execute(
        'INSERT INTO order_lines (order_id, sku, quantity) VALUES '
        '("order1", "RED-CHAIR", 12),'
        '("order1", "RED-TABLE", 13),'
        '("order2", "BLUE-LIPSTICK", 14)'
    )
    expected = [
        model.OrderLine("order1", "RED-CHAIR", 12),
        model.OrderLine("order1", "RED-TABLE", 13),
        model.OrderLine("order2", "BLUE-LIPSTICK", 14),
    ]
    assert session.query(model.OrderLine).all() == expected
```

*Console error* for `pipenv run pytest test_orm.py`

```bash
============================= test session starts =============================
platform linux -- Python 3.7.6, pytest-5.4.1, py-1.8.1, pluggy-0.13.1
rootdir: /home/[redacted]/Documents/architecture-patterns-python
collected 1 item                                                              

test_orm.py F                                                           [100%]

================================== FAILURES ===================================
____________________ test_orderline_mapper_can_load_lines _____________________

session = <sqlalchemy.orm.session.Session object at 0x7fd919ac5bd0>

    def test_orderline_mapper_can_load_lines(session):
        session.execute(
            'INSERT INTO order_lines (order_id, sku, quantity) VALUES '
            '("order1", "RED-CHAIR", 12),'
            '("order1", "RED-TABLE", 13),'
            '("order2", "BLUE-LIPSTICK", 14)'
        )
        expected = [
>           model.OrderLine("order1", "RED-CHAIR", 12),
            model.OrderLine("order1", "RED-TABLE", 13),
            model.OrderLine("order2", "BLUE-LIPSTICK", 14),
        ]

test_orm.py:13: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
<string>:2: in __init__
    ???
../../.local/share/virtualenvs/architecture-patterns-python-Qi2y0bev/lib64/python3.7/site-packages/sqlalchemy/orm/instrumentation.py:377: in _new_state_if_none
    self._state_setter(instance, state)
<string>:1: in set
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <[AttributeError("'OrderLine' object has no attribute '_sa_instance_state'") raised in repr()] OrderLine object at 0x7fd919a8cf50>
name = '_sa_instance_state'
value = <sqlalchemy.orm.state.InstanceState object at 0x7fd9198f7490>

>   ???
E   dataclasses.FrozenInstanceError: cannot assign to field '_sa_instance_state'

<string>:4: FrozenInstanceError
=========================== short test summary info ===========================
FAILED test_orm.py::test_orderline_mapper_can_load_lines - dataclasses.Froze...
============================== 1 failed in 0.06s ==============================
```


**Additional Questions**

I understand the overlying logic and what these files are doing, but correct my if my rudimentary understanding is lacking.<br>
1. `conftest.py` (used for all pytest config) is setting up a `session` fixture, which basically sets up a temporary database in memory - using start and clear mappers to ensure that the orm model definitions are binding to the db isntance.<br>
2. `model.py` simply a dataclass used to represent an atomic `OrderLine` object.<br>
3. `test_orm.py` class for pytest to supply the `session` fixture, in order to `setup, execute, teardown` a db explicitly for the purpose of running tests.

My Comments
===========
I see that in the `local_db()` fixture, you call `metadata.create_all(engine)`,  so I assume that somewhere in your code you have a `Table("order_lines", metadata, ...)` call or  a class somewhere like `class OrderLine(Base): ...`. If you created a `Table` object you need to [map `model.OrderLine` to the `Table`](https://docs.sqlalchemy.org/en/13/orm/mapping_styles.html#classical-mappings).  If you have an ORM (`Base`) class, you need to use that to query the database through the session. Need more info, try to create a fully self enclosed example that reproduces the problem.

However, having said that you need to map model.OrderLine, the fact that it is a frozen dataclass instance means that you can't add attributes to it and that is really what your error states: sqlalchemy is trying to treat it as a mapped class and mutate its state, which the frozen dataclass won't allow. That's why I'm asking for a more complete example, the error that is manifesting here isn't at the root of your problem.

Where I've Left It
==================
The example code reproduces the problem. Set up the environment and run `pytest test_orm.py`.

I haven't answered as there is still too many questions as to how the OP has arrived at this point. How is the table getting created in the `metadata` such that `metadata.create_all()` being executed in the `local_db()` fixture creates the table. Why is the OP using frozen dataclass instances to create test cases for using `==` comparison to an expected collection of ORM instances from the query? On what basis should querying through the session with the dataclass work? I.e., should the dataclasses be mapped to an already existing table, or is the OP using the dataclasses in error when there is an ORM class lying around in the codebase somewhere else that should be used to build the query instead.