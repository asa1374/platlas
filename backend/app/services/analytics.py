from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from redis.asyncio import Redis
from sqlalchemy import and_, func, select, update

from app.core.config import get_settings
from app.db.models import Collection, MetricEntityType, MetricsDaily
from app.db.session import SessionLocal
from app.schemas.analytics import AnalyticsDashboard
from app.schemas.collection import CollectionMetrics

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class QueuedEvent:
    entity_type: str
    entity_id: int
    event_type: str
    occurred_at: datetime


class AnalyticsService:
    def __init__(self) -> None:
        settings = get_settings()
        self.redis: Redis = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=False)
        self.queue_key = "analytics:events"
        self._consumer_task: Optional[asyncio.Task[Any]] = None
        self._scheduler_task: Optional[asyncio.Task[Any]] = None
        self._running = False
        self.trending_window_days = 7

    async def enqueue_event(self, payload: Dict[str, Any]) -> None:
        data = json.dumps(payload, default=str)
        await self.redis.rpush(self.queue_key, data)

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        loop = asyncio.get_running_loop()
        self._consumer_task = loop.create_task(self._consume_loop())
        self._scheduler_task = loop.create_task(self._scheduler_loop())

    async def shutdown(self) -> None:
        self._running = False
        tasks = [self._consumer_task, self._scheduler_task]
        for task in tasks:
            if task is None:
                continue
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception:  # pragma: no cover - defensive
                logger.exception("Analytics background task shutdown failed")
        self._consumer_task = None
        self._scheduler_task = None
        try:
            await self.redis.aclose()
        except Exception:  # pragma: no cover - defensive
            logger.exception("Failed to close redis connection")

    async def _consume_loop(self) -> None:
        try:
            while self._running:
                item = await self.redis.blpop(self.queue_key, timeout=1)
                if not item:
                    continue
                _, raw = item
                try:
                    payload = json.loads(raw)
                    event = self._parse_event(payload)
                except Exception:  # pragma: no cover - defensive
                    logger.exception("Invalid analytics payload: %s", raw)
                    continue
                await asyncio.to_thread(self._apply_event, event)
        except asyncio.CancelledError:
            raise
        except Exception:  # pragma: no cover - defensive
            logger.exception("Analytics consumer crashed")
        finally:
            logger.info("Analytics consumer stopped")

    async def _scheduler_loop(self) -> None:
        try:
            # run once on startup
            await asyncio.to_thread(self._calculate_trending_scores)
            while self._running:
                now = datetime.now(timezone.utc)
                seconds = self._seconds_until_next_run(now)
                await asyncio.sleep(seconds)
                await asyncio.to_thread(self._calculate_trending_scores)
        except asyncio.CancelledError:
            raise
        except Exception:  # pragma: no cover - defensive
            logger.exception("Trending scheduler crashed")
        finally:
            logger.info("Trending scheduler stopped")

    def _apply_event(self, event: QueuedEvent) -> None:
        session = SessionLocal()
        try:
            metrics = session.execute(
                select(MetricsDaily).where(
                    and_(
                        MetricsDaily.entity_type == MetricEntityType(event.entity_type),
                        MetricsDaily.entity_id == event.entity_id,
                        MetricsDaily.date == event.occurred_at.date(),
                    )
                )
            ).scalar_one_or_none()

            if metrics is None:
                metrics = MetricsDaily(
                    entity_type=MetricEntityType(event.entity_type),
                    entity_id=event.entity_id,
                    date=event.occurred_at.date(),
                    views=0,
                    clicks=0,
                )

            if event.event_type == "view":
                metrics.views += 1
            elif event.event_type == "click":
                metrics.clicks += 1

            session.add(metrics)
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Failed to persist analytics event")
        finally:
            session.close()

    def _calculate_trending_scores(self) -> None:
        session = SessionLocal()
        try:
            today = date.today()
            start_date = today - timedelta(days=self.trending_window_days - 1)
            rows: List[MetricsDaily] = (
                session.execute(
                    select(MetricsDaily)
                    .where(MetricsDaily.entity_type == MetricEntityType.COLLECTION)
                    .where(MetricsDaily.date >= start_date)
                )
                .scalars()
                .all()
            )

            scores: Dict[int, float] = defaultdict(float)
            for row in rows:
                age = (today - row.date).days
                decay = 1 / (age + 1)
                base_score = row.views + (row.clicks * 2)
                scores[row.entity_id] += base_score * decay

            session.execute(update(Collection).values(trending_score=0.0))
            if scores:
                for collection_id, value in scores.items():
                    session.execute(
                        update(Collection)
                        .where(Collection.id == collection_id)
                        .values(trending_score=value)
                    )
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Failed to calculate trending scores")
        finally:
            session.close()

    async def get_dashboard(self, days: int = 14, top_limit: int = 5) -> AnalyticsDashboard:
        return await asyncio.to_thread(self._build_dashboard, days, top_limit)

    def _build_dashboard(self, days: int, top_limit: int) -> AnalyticsDashboard:
        session = SessionLocal()
        try:
            today = date.today()
            start_date = today - timedelta(days=days - 1)

            daily_rows = (
                session.execute(
                    select(MetricsDaily.date, func.sum(MetricsDaily.views), func.sum(MetricsDaily.clicks))
                    .where(MetricsDaily.date >= start_date)
                    .group_by(MetricsDaily.date)
                    .order_by(MetricsDaily.date.asc())
                )
                .all()
            )
            daily_map: Dict[date, Dict[str, int]] = {row[0]: {"views": int(row[1] or 0), "clicks": int(row[2] or 0)} for row in daily_rows}

            daily_points = []
            for index in range(days):
                current = start_date + timedelta(days=index)
                values = daily_map.get(current, {"views": 0, "clicks": 0})
                daily_points.append({
                    "date": current,
                    "views": values["views"],
                    "clicks": values["clicks"],
                })

            sum_views = func.coalesce(func.sum(MetricsDaily.views), 0)
            sum_clicks = func.coalesce(func.sum(MetricsDaily.clicks), 0)
            top_rows = (
                session.execute(
                    select(
                        Collection.id,
                        Collection.slug,
                        Collection.title,
                        sum_views.label("views"),
                        sum_clicks.label("clicks"),
                        Collection.trending_score,
                    )
                    .outerjoin(
                        MetricsDaily,
                        and_(
                            MetricsDaily.entity_type == MetricEntityType.COLLECTION,
                            MetricsDaily.entity_id == Collection.id,
                            MetricsDaily.date >= start_date,
                        ),
                    )
                    .group_by(Collection.id)
                    .order_by(Collection.trending_score.desc(), sum_views.desc())
                    .limit(top_limit)
                )
                .all()
            )

            top_collections = [
                {
                    "collection_id": row[0],
                    "slug": row[1],
                    "title": row[2],
                    "views": int(row[3] or 0),
                    "clicks": int(row[4] or 0),
                    "trending_score": float(row[5] or 0.0),
                }
                for row in top_rows
            ]

            return AnalyticsDashboard(daily=daily_points, top_collections=top_collections)
        finally:
            session.close()

    @staticmethod
    def _seconds_until_next_run(now: datetime) -> float:
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return max((tomorrow - now).total_seconds(), 60.0)

    @staticmethod
    def _parse_event(payload: Dict[str, Any]) -> QueuedEvent:
        entity_type = str(payload.get("entity_type", "")).lower()
        event_type = str(payload.get("event_type", "")).lower()
        entity_id = int(payload.get("entity_id", 0))
        occurred_at_raw = payload.get("occurred_at")

        if entity_type not in {"collection", "platform"}:
            raise ValueError("invalid entity type")
        if event_type not in {"view", "click"}:
            raise ValueError("invalid event type")
        if entity_id <= 0:
            raise ValueError("invalid entity id")

        if occurred_at_raw:
            occurred_at = datetime.fromisoformat(str(occurred_at_raw))
            if occurred_at.tzinfo is None:
                occurred_at = occurred_at.replace(tzinfo=timezone.utc)
            else:
                occurred_at = occurred_at.astimezone(timezone.utc)
        else:
            occurred_at = datetime.now(timezone.utc)

        return QueuedEvent(
            entity_type=entity_type,
            entity_id=entity_id,
            event_type=event_type,
            occurred_at=occurred_at,
        )


analytics = AnalyticsService()


def fetch_collection_metrics(session, collection_ids: List[int]) -> Dict[int, CollectionMetrics]:
    if not collection_ids:
        return {}
    rows = (
        session.execute(
            select(
                MetricsDaily.entity_id,
                func.sum(MetricsDaily.views),
                func.sum(MetricsDaily.clicks),
            )
            .where(MetricsDaily.entity_type == MetricEntityType.COLLECTION)
            .where(MetricsDaily.entity_id.in_(collection_ids))
            .group_by(MetricsDaily.entity_id)
        )
        .all()
    )
    return {
        row[0]: CollectionMetrics(views=int(row[1] or 0), clicks=int(row[2] or 0))
        for row in rows
    }
