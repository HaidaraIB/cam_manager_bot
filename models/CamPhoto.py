import sqlalchemy as sa
from sqlalchemy.orm import Session, relationship
from models.DB import (
    Base,
    connect_and_close,
    lock_and_release,
)


class CamPhoto(Base):
    __tablename__ = "cam_photos"
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    cam_id = sa.Column(sa.Integer, sa.ForeignKey("cameras.id", ondelete="CASCADE"))
    path = sa.Column(sa.String)
    file_id = sa.Column(sa.String)

    cam = relationship("Camera", back_populates="photos")

    @classmethod
    @lock_and_release
    async def add(
        cls,
        cam_id: int,
        path:str,
        file_id: str,
        s: Session = None,
    ):
        s.execute(
            sa.insert(cls).values(
                cam_id=cam_id,
                path=path,
                file_id=file_id,
            )
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

    @classmethod
    @lock_and_release
    async def update(cls, cam_photo_id: int, attrs: list, new_vals: list, s: Session = None):
        s.query(cls).filter_by(id=cam_photo_id).update(
            dict(zip([getattr(cls, attr) for attr in attrs], new_vals))
        )