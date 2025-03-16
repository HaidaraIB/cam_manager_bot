import sqlalchemy as sa
from sqlalchemy.orm import Session
from models.AlertType import AlertType
from models.AlertDest import AlertDest
from models.DB import (
    Base,
    connect_and_close,
    lock_and_release,
)


class Alert(Base):
    __tablename__ = "alerts"
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    alert_type = sa.Column(sa.Enum(AlertType), unique=True)
    is_on = sa.Column(sa.Boolean, default=False)
    dest = sa.Column(sa.Enum(AlertDest), default=AlertDest.NONE)

    @classmethod
    @lock_and_release
    async def add(cls, alert_type: AlertType, s: Session = None):
        s.execute(sa.insert(cls).values(alert_type=alert_type).prefix_with("OR IGNORE"))

    @classmethod
    @lock_and_release
    async def update(
        cls, alert_id: int, attrs: list, new_vals: list, s: Session = None
    ):
        s.query(cls).filter_by(id=alert_id).update(
            dict(zip([getattr(cls, attr) for attr in attrs], new_vals))
        )

    @classmethod
    @connect_and_close
    def get_by(
        cls,
        attr=None,
        val=None,
        all: bool = False,
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
            try:
                return list(map(lambda x: x[0], res.tuples().all()))
            except:
                pass
