from pathlib import Path

from httpx import Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from scrapers import main


def factory() -> tuple[Client, Session]:
    db_path = Path(__file__).parent.joinpath('database.sqlite3').resolve()
    engine = create_engine('sqlite:///%s' % db_path)
    session = Client()
    DBSession = sessionmaker(bind=engine)
    db = DBSession()
    return session, db


if __name__ == '__main__':
    session, db = factory()
    try:
        main(db=db, session=session)
    finally:
        session.close()
        db.close()
