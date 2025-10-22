"use client";

import { useCallback, useEffect, useMemo, useRef } from "react";

import { logAnalyticsEvent, type AnalyticsEntityType } from "@/lib/analytics";

interface UseAnalyticsEventOptions {
  metadata?: Record<string, string>;
  disableView?: boolean;
}

export function useAnalyticsEvent(
  entityType: AnalyticsEntityType,
  entityId: number,
  options: UseAnalyticsEventOptions = {}
) {
  const hasLoggedViewRef = useRef(false);
  const metadata = useMemo(() => options.metadata, [options.metadata]);

  useEffect(() => {
    if (options.disableView) {
      return;
    }
    if (hasLoggedViewRef.current) {
      return;
    }
    hasLoggedViewRef.current = true;

    const timeout = window.setTimeout(() => {
      void logAnalyticsEvent({
        entity_type: entityType,
        entity_id: entityId,
        event_type: "view",
        metadata,
      });
    }, 200);

    return () => window.clearTimeout(timeout);
  }, [entityId, entityType, metadata, options.disableView]);

  const logClick = useCallback(() => {
    void logAnalyticsEvent({
      entity_type: entityType,
      entity_id: entityId,
      event_type: "click",
      metadata,
    });
  }, [entityId, entityType, metadata]);

  return { logClick };
}
