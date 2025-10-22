"use client";

import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  adminLogin,
  approveSubmission,
  fetchAdminSubmissions,
  rejectSubmission,
  type SubmissionResponse,
} from "@/lib/submissions";

const statusLabel: Record<string, string> = {
  pending: "검토 중",
  approved: "승인됨",
  rejected: "거절됨",
};

export default function AdminSubmissionsPage() {
  const [submissions, setSubmissions] = useState<SubmissionResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loginForm, setLoginForm] = useState({ username: "", password: "" });
  const [isLoginSubmitting, setIsLoginSubmitting] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const loadSubmissions = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await fetchAdminSubmissions();
      setSubmissions(data.items);
      setIsAuthenticated(true);
      setError(null);
    } catch (loadError) {
      if (loadError instanceof Error && loadError.message === "UNAUTHORIZED") {
        setIsAuthenticated(false);
      } else {
        setError(loadError instanceof Error ? loadError.message : "제출 목록을 불러오는 중 오류가 발생했습니다.");
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadSubmissions();
  }, [loadSubmissions]);

  const handleLoginSubmit = useCallback(
    async (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      setIsLoginSubmitting(true);
      setError(null);
      setActionMessage(null);
      try {
        await adminLogin({
          username: loginForm.username.trim(),
          password: loginForm.password,
        });
        setIsAuthenticated(true);
        setLoginForm({ username: "", password: "" });
        await loadSubmissions();
        setActionMessage("로그인되었습니다.");
      } catch (loginError) {
        setError(loginError instanceof Error ? loginError.message : "로그인 중 오류가 발생했습니다.");
      } finally {
        setIsLoginSubmitting(false);
      }
    },
    [loadSubmissions, loginForm]
  );

  const handleApprove = useCallback(
    async (submission: SubmissionResponse) => {
      try {
        await approveSubmission(submission.id);
        await loadSubmissions();
        setActionMessage(`${submission.platform_name} 제출이 승인되었습니다.`);
      } catch (approveError) {
        setError(approveError instanceof Error ? approveError.message : "승인 중 오류가 발생했습니다.");
      }
    },
    [loadSubmissions]
  );

  const handleReject = useCallback(
    async (submission: SubmissionResponse) => {
      const reason = window.prompt("거절 사유를 입력하세요.", submission.rejection_reason ?? "");
      if (!reason) {
        return;
      }
      try {
        await rejectSubmission(submission.id, reason);
        await loadSubmissions();
        setActionMessage(`${submission.platform_name} 제출이 거절되었습니다.`);
      } catch (rejectError) {
        setError(rejectError instanceof Error ? rejectError.message : "거절 중 오류가 발생했습니다.");
      }
    },
    [loadSubmissions]
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
              <Button className="w-full" type="submit" disabled={isLoginSubmitting}>
                {isLoginSubmitting ? "로그인 중..." : "로그인"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6 py-12">
      <div>
        <h1 className="text-3xl font-bold">플랫폼 제출 관리</h1>
        <p className="text-muted-foreground">사용자 제출 목록을 확인하고 승인 또는 거절할 수 있습니다.</p>
      </div>
      {actionMessage ? <p className="rounded-md bg-emerald-50 px-4 py-2 text-sm text-emerald-700">{actionMessage}</p> : null}
      {error ? <p className="text-sm text-destructive">{error}</p> : null}
      {isLoading ? (
        <p className="text-muted-foreground">불러오는 중...</p>
      ) : submissions.length === 0 ? (
        <p className="text-muted-foreground">현재 검토할 제출이 없습니다.</p>
      ) : (
        <div className="grid gap-4">
          {submissions.map((submission) => (
            <Card key={submission.id}>
              <CardHeader>
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <CardTitle>{submission.platform_name}</CardTitle>
                  <span className="text-sm font-medium">
                    상태: {statusLabel[submission.status] ?? submission.status}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">
                  제출자: {submission.submitter_name} ({submission.submitter_email}) · {new Date(submission.created_at).toLocaleString()}
                </p>
              </CardHeader>
              <CardContent className="space-y-4">
                {submission.description ? (
                  <p className="whitespace-pre-wrap text-sm text-muted-foreground">{submission.description}</p>
                ) : null}
                <div className="grid gap-2 text-sm">
                  {submission.website_url ? (
                    <a className="text-primary underline" href={submission.website_url} target="_blank" rel="noreferrer">
                      공식 웹사이트 방문
                    </a>
                  ) : null}
                  {submission.web_url ? (
                    <a className="text-primary underline" href={submission.web_url} target="_blank" rel="noreferrer">
                      웹 앱 열기
                    </a>
                  ) : null}
                  {submission.ios_url ? (
                    <a className="text-primary underline" href={submission.ios_url} target="_blank" rel="noreferrer">
                      iOS 앱 링크
                    </a>
                  ) : null}
                  {submission.android_url ? (
                    <a className="text-primary underline" href={submission.android_url} target="_blank" rel="noreferrer">
                      Android 앱 링크
                    </a>
                  ) : null}
                  {submission.screenshot_url ? (
                    <a className="text-primary underline" href={submission.screenshot_url} target="_blank" rel="noreferrer">
                      업로드된 스크린샷 보기
                    </a>
                  ) : null}
                  {submission.platform_id ? (
                    <span className="text-muted-foreground">
                      플랫폼 ID: {submission.platform_id}
                    </span>
                  ) : null}
                  {submission.rejection_reason ? (
                    <span className="text-destructive">
                      거절 사유: {submission.rejection_reason}
                    </span>
                  ) : null}
                </div>
                {submission.status === "pending" ? (
                  <div className="flex flex-wrap gap-3">
                    <Button onClick={() => handleApprove(submission)}>승인</Button>
                    <Button variant="outline" onClick={() => handleReject(submission)}>
                      거절
                    </Button>
                  </div>
                ) : null}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
