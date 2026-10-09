import datetime as dt

from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import DbSession
from app.models import PeriodReport, ReportKind
from app.schemas.report import ReportCreate, ReportRead, ReportUpdate
from app.services.periods import period_bounds

router = APIRouter(prefix="/reports", tags=["reports"])


def get_report_or_404(db: DbSession, kind: ReportKind, anchor: dt.date) -> PeriodReport:
    """Ищет отчёт по виду и любой дате внутри периода."""
    period_start, _ = period_bounds(kind, anchor)
    report = db.scalars(
        select(PeriodReport).where(
            PeriodReport.kind == kind, PeriodReport.period_start == period_start
        )
    ).one_or_none()
    if report is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Report not found")
    return report


@router.get("", response_model=list[ReportRead])
def list_reports(
    db: DbSession,
    kind: ReportKind | None = None,
    date_from: dt.date | None = Query(default=None, alias="from"),
    date_to: dt.date | None = Query(default=None, alias="to"),
):
    """Отчёты от новых к старым. `from`/`to` — отчёты, чей период пересекается с диапазоном."""
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "'from' must not be after 'to'")
    stmt = select(PeriodReport).order_by(PeriodReport.period_start.desc(), PeriodReport.kind)
    if kind is not None:
        stmt = stmt.where(PeriodReport.kind == kind)
    if date_from is not None:
        stmt = stmt.where(PeriodReport.period_end >= date_from)
    if date_to is not None:
        stmt = stmt.where(PeriodReport.period_start <= date_to)
    return db.scalars(stmt).all()


@router.get("/{kind}/{anchor}", response_model=ReportRead)
def get_report(kind: ReportKind, anchor: dt.date, db: DbSession):
    """Например, `/reports/week/2026-10-07` — отчёт за неделю 05-11 октября."""
    return get_report_or_404(db, kind, anchor)


@router.post("", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
def create_report(payload: ReportCreate, db: DbSession):
    period_start, period_end = period_bounds(payload.kind, payload.date)
    report = PeriodReport(
        kind=payload.kind, period_start=period_start, period_end=period_end, text=payload.text
    )
    db.add(report)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"{payload.kind.value.capitalize()} report for this period already exists"
        )
    db.refresh(report)
    return report


@router.patch("/{kind}/{anchor}", response_model=ReportRead)
def update_report(kind: ReportKind, anchor: dt.date, payload: ReportUpdate, db: DbSession):
    report = get_report_or_404(db, kind, anchor)
    report.text = payload.text
    db.commit()
    db.refresh(report)
    return report


@router.delete("/{kind}/{anchor}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(kind: ReportKind, anchor: dt.date, db: DbSession):
    report = get_report_or_404(db, kind, anchor)
    db.delete(report)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
