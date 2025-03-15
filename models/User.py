import sqlalchemy as sa
from models.DB import connect_and_close, lock_and_release
from sqlalchemy.orm import Session
from models.BaseUser import BaseUser


class User(BaseUser):
    is_banned = sa.Column(sa.Boolean, default=0)
    __tablename__ = "users"
    __table_args__ = (sa.PrimaryKeyConstraint("id", name="_id_user"),)

    @classmethod
    @lock_and_release
    async def add_new_user(
        cls, user_id: int, username: str, name: str, s: Session = None
    ):
        s.execute(
            sa.insert(cls)
            .values(id=user_id, username=username if username else "", name=name)
            .prefix_with("OR IGNORE")
        )

    @classmethod
    @connect_and_close
    def get_users(cls, user_id: int = None, s: Session = None):
        if user_id:
            res = s.execute(sa.select(cls).where(cls.id == user_id))
            try:
                return res.fetchone().t[0]
            except:
                return
        res = s.execute(sa.select(cls))
        try:
            return list(map(lambda x: x[0], res.tuples().all()))
        except:
            pass

    @classmethod
    @lock_and_release
    async def set_banned(cls, user_id: int, banned: bool, s: Session = None):
        s.query(cls).filter_by(id=user_id).update(
            {
                cls.is_banned: banned,
            },
        )

    @classmethod
    @lock_and_release
    async def delete(cls, user_id: int, s: Session = None):
        s.execute(sa.delete(cls).where(cls.id == user_id))
