from __future__ import annotations

import pytest
from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture
def local_db() -> Engine:
    metadata = MetaData()
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(local_db: Engine) -> Session:
    return sessionmaker(bind=local_db)()  # type:ignore
