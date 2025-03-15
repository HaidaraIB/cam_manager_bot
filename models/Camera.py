import sqlalchemy as sa
from sqlalchemy.orm import Session
from models.DB import (
    Base,
    connect_and_close,
    lock_and_release,
)


class Camera(Base):
    __tablename__ = "cameras"
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    name = sa.Column(sa.String)
    photo = sa.Column(sa.String)
    ip = sa.Column(sa.String)
    port = sa.Column(sa.Integer)
    admin_user = sa.Column(sa.String)
    admin_password = sa.Column(sa.String)
    user = sa.Column(sa.String)
    user_password = sa.Column(sa.String)
    cam_type = sa.Column(sa.String)
    status = sa.Column(sa.String)
    location = sa.Column(sa.String)
    serial = sa.Column(sa.String)

    @classmethod
    @lock_and_release
    async def add(
        cls,
        cam_data: dict,
        s: Session = None,
    ):
        res = s.execute(
            sa.insert(cls).values(
                name=cam_data["name"],
                photo=cam_data["photo"],
                ip=cam_data["ip"],
                port=cam_data["port"],
                admin_user=cam_data["admin_user"],
                admin_password=cam_data["admin_pass"],
                user=cam_data["user"],
                user_password=cam_data["user_pass"],
                cam_type=cam_data["cam_type"],
                status=cam_data["status"],
                location=cam_data["location"],
                serial=cam_data["serial"],
            )
        )
        return res.lastrowid

    @classmethod
    @lock_and_release
    async def delete(cls, cam_id: int, s: Session = None):
        s.execute(sa.delete(cls).where(cls.id == cam_id))

    @classmethod
    @lock_and_release
    async def update(cls, cam_id: int, attrs: list, new_vals: list, s: Session = None):
        s.query(cls).filter_by(id=cam_id).update(
            dict(zip([getattr(cls, attr) for attr in attrs], new_vals))
        )

    @classmethod
    @connect_and_close
    def get_by(
        cls,
        attr=None,
        val=None,
        all: bool = False,
        last: bool = False,
        s: Session = None,
    ):
        if attr and val:
            res = s.execute(sa.select(cls).where(getattr(cls, attr) == val))
            try:
                if all:
                    return list(map(lambda x: x[0], res.tuples().all()))
                return res.fetchone().t[0]
            except:
                pass
        else:
            res = s.execute(sa.select(cls))
            cams = list(map(lambda x: x[0], res.tuples().all()))
            try:
                if last:
                    return cams[-1]
                return cams
            except:
                return
