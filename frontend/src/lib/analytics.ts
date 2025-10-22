import { API_BASE_URL, type ApiResponse } from "@/lib/utils";

export type AnalyticsEntityType = "collection" | "platform";
export type AnalyticsEventType = "view" | "click";

export interface AnalyticsEventPayload {
  entity_type: AnalyticsEntityType;
  entity_id: number;
  event_type: AnalyticsEventType;
  occurred_at?: string;
  metadata?: Record<string, string>;
}

export interface DailyMetricPoint {
  date: string;
  views: number;
  clicks: number;
}

export interface TopCollectionMetric {
  collection_id: number;
  slug: string;
  title: string;
  views: number;
  clicks: number;
  trending_score: number;
}

export interface AnalyticsDashboardData {
  daily: DailyMetricPoint[];
  top_collections: TopCollectionMetric[];
}

export interface AnalyticsDashboardResponse extends ApiResponse<AnalyticsDashboardData> {}

export async function logAnalyticsEvent(payload: AnalyticsEventPayload): Promise<void> {
  await fetch(`${API_BASE_URL}/analytics/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    keepalive: true,
  });
}

export async function fetchAnalyticsDashboard(
  days = 14,
  topLimit = 5
): Promise<AnalyticsDashboardData> {
  const params = new URLSearchParams({ days: String(days), top_limit: String(topLimit) });
  const response = await fetch(`${API_BASE_URL}/analytics/dashboard?${params.toString()}`, {
    credentials: "include",
  });

  if (response.status === 401) {
    throw new Error("UNAUTHORIZED");
  }

  if (!response.ok) {
    throw new Error("대시보드 메트릭을 불러오지 못했습니다.");
  }

  const data = (await response.json()) as AnalyticsDashboardResponse;
  if (!data.data) {
    throw new Error(data.message ?? "대시보드 응답이 올바르지 않습니다.");
  }

  return data.data;
}
