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
    cam_id = sa.Column(sa.Integer, sa.ForeignKey("cameras.id"))
    file_id = sa.Column(sa.String)
    file_unique_id = sa.Column(sa.String)
    width = sa.Column(sa.Integer)
    height = sa.Column(sa.Integer)

    cam = relationship("Camera", back_populates="photos")

    @classmethod
    @lock_and_release
    async def add(
        cls,
        cam_id: int,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        s: Session = None,
    ):
        s.execute(
            sa.insert(cls).values(
                cam_id=cam_id,
                file_id=file_id,
                file_unique_id=file_unique_id,
                width=width,
                height=height,
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
