from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, Session
import traceback
from asyncio import Lock
from models import *

lock = Lock()
Base = declarative_base()
engine = create_engine(
    "sqlite:///data/database.sqlite3", connect_args={"check_same_thread": False}
)


def create_tables():
    s = Session(bind=engine, autoflush=True)
    s.execute(text("PRAGMA foreign_keys=ON"))
    s.commit()
    s.close()
    Base.metadata.create_all(engine)


def lock_and_release(func):
    async def wrapper(*args, **kwargs):
        try:
            await lock.acquire()
            s = Session(bind=engine, autoflush=True)
            result = await func(*args, **kwargs, s=s)
            s.commit()
            if result:
                return result
        except Exception as e:
            print(e)
            with open("errors.txt", "a", encoding="utf-8") as f:
                f.write(f"{traceback.format_exc()}\n{'-'*100}\n\n\n")
        finally:
            s.close()
            lock.release()

    return wrapper


def connect_and_close(func):
    def wrapper(*args, **kwargs):
        s = Session(bind=engine, autoflush=True)
        result = func(*args, **kwargs, s=s)
        s.close()
        return result

    return wrapper
