"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { adminLogin } from "@/lib/submissions";
import {
  fetchAnalyticsDashboard,
  type AnalyticsDashboardData,
  type DailyMetricPoint,
} from "@/lib/analytics";

interface LoginFormState {
  username: string;
  password: string;
}

export default function AdminMetricsPage() {
  const [loginForm, setLoginForm] = useState<LoginFormState>({ username: "", password: "" });
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [dashboard, setDashboard] = useState<AnalyticsDashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadDashboard = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await fetchAnalyticsDashboard();
      setDashboard(data);
      setIsAuthenticated(true);
      setError(null);
    } catch (dashboardError) {
      if (dashboardError instanceof Error && dashboardError.message === "UNAUTHORIZED") {
        setIsAuthenticated(false);
      } else {
        setError(
          dashboardError instanceof Error
            ? dashboardError.message
            : "대시보드 데이터를 불러오는 중 오류가 발생했습니다.",
        );
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  const handleLoginSubmit = useCallback(
    async (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      setIsSubmitting(true);
      setError(null);
      try {
        await adminLogin({
          username: loginForm.username.trim(),
          password: loginForm.password,
        });
        setIsAuthenticated(true);
        setLoginForm({ username: "", password: "" });
        await loadDashboard();
      } catch (loginError) {
        setError(loginError instanceof Error ? loginError.message : "로그인에 실패했습니다.");
      } finally {
        setIsSubmitting(false);
      }
    },
    [loadDashboard, loginForm]
  );

  if (!isAuthenticated) {
    return (
      <div className="mx-auto max-w-md py-16">
        <Card>
          <CardHeader>
            <CardTitle>어드민 로그인</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={handleLoginSubmit}>
              <div className="space-y-2">
                <Label htmlFor="username">아이디</Label>
                <Input
                  id="username"
                  value={loginForm.username}
                  onChange={(event) => setLoginForm((prev) => ({ ...prev, username: event.target.value }))}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">비밀번호</Label>
                <Input
                  id="password"
                  type="password"
                  value={loginForm.password}
                  onChange={(event) => setLoginForm((prev) => ({ ...prev, password: event.target.value }))}
                  required
                />
              </div>
              {error ? <p className="text-sm text-destructive">{error}</p> : null}
              <Button className="w-full" type="submit" disabled={isSubmitting}>
                {isSubmitting ? "로그인 중..." : "로그인"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8 py-12">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold">트렌드 메트릭 대시보드</h1>
        <p className="text-muted-foreground">조회 및 클릭 추이를 확인하고 컬렉션 추천 전략을 최적화하세요.</p>
      </div>
      {error ? <p className="text-sm text-destructive">{error}</p> : null}
      {isLoading ? (
        <p className="text-muted-foreground">대시보드를 불러오는 중입니다...</p>
      ) : dashboard ? (
        <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>지난 2주 주요 지표</CardTitle>
            </CardHeader>
            <CardContent>
              <DailyMetricsChart points={dashboard.daily} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>상위 컬렉션</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {dashboard.top_collections.length === 0 ? (
                <p className="text-sm text-muted-foreground">최근 데이터가 없습니다.</p>
              ) : (
                <ul className="space-y-3">
                  {dashboard.top_collections.map((collection, index) => (
                    <li
                      key={collection.collection_id}
                      className="flex items-center justify-between rounded-lg border bg-card/60 px-4 py-3"
                    >
                      <div>
                        <p className="font-semibold">
                          {index + 1}. {collection.title}
                        </p>
                        <p className="text-xs text-muted-foreground">트렌드 지수 {Math.round(collection.trending_score)}</p>
                      </div>
                      <div className="text-right text-xs text-muted-foreground">
                        <p>조회수 {collection.views.toLocaleString()}</p>
                        <p>클릭 {collection.clicks.toLocaleString()}</p>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
      ) : (
        <p className="text-muted-foreground">대시보드 데이터를 찾을 수 없습니다.</p>
      )}
    </div>
  );
}

function DailyMetricsChart({ points }: { points: DailyMetricPoint[] }) {
  const formattedPoints = useMemo(() => points.slice(-14), [points]);
  const maxValue = useMemo(() => {
    if (formattedPoints.length === 0) {
      return 1;
    }
    return Math.max(
      ...formattedPoints.map((point) => Math.max(point.views, point.clicks)),
      1,
    );
  }, [formattedPoints]);

  return (
    <div className="space-y-4">
      <div className="flex h-48 items-end gap-2">
        {formattedPoints.map((point) => {
          const viewHeight = (point.views / maxValue) * 100;
          const clickHeight = (point.clicks / maxValue) * 100;
          const dateLabel = new Date(point.date).toLocaleDateString();
          return (
            <div key={point.date} className="flex flex-1 flex-col items-center gap-2 text-xs">
              <div className="flex h-32 w-full items-end gap-1 rounded bg-muted/60 p-1">
                <div
                  className="w-1.5 rounded bg-primary"
                  style={{ height: `${Math.max(viewHeight, 4)}%` }}
                  title={`조회수 ${point.views.toLocaleString()}`}
                />
                <div
                  className="w-1.5 rounded bg-emerald-500/80"
                  style={{ height: `${Math.max(clickHeight, 4)}%` }}
                  title={`클릭 ${point.clicks.toLocaleString()}`}
                />
              </div>
              <span className="text-[10px] text-muted-foreground">{dateLabel}</span>
            </div>
          );
        })}
      </div>
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          <span className="inline-block h-2 w-2 rounded-full bg-primary" />
          <span>조회수</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-block h-2 w-2 rounded-full bg-emerald-500/80" />
          <span>클릭</span>
        </div>
      </div>
    </div>
  );
}
