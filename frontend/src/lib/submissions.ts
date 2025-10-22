import { API_BASE_URL, type ApiResponse } from "@/lib/utils";

export type SubmissionStatus = "pending" | "approved" | "rejected";

export interface SubmissionPayload {
  submitter_name: string;
  submitter_email: string;
  platform_name: string;
  description?: string;
  website_url?: string;
  ios_url?: string;
  android_url?: string;
  web_url?: string;
  screenshot_url?: string;
  recaptchaToken?: string;
}

export interface SubmissionResponse {
  id: number;
  submitter_name: string;
  submitter_email: string;
  platform_name: string;
  description?: string | null;
  website_url?: string | null;
  ios_url?: string | null;
  android_url?: string | null;
  web_url?: string | null;
  screenshot_url?: string | null;
  status: SubmissionStatus;
  rejection_reason?: string | null;
  platform_id?: number | null;
  created_at: string;
  updated_at: string;
  approved_at?: string | null;
  rejected_at?: string | null;
}

export interface PresignedUploadPayload {
  filename: string;
  contentType?: string;
}

export interface PresignedUploadResponse {
  uploadUrl: string;
  fileUrl: string;
}

export async function requestSubmissionUploadUrl(
  payload: PresignedUploadPayload
): Promise<PresignedUploadResponse> {
  const response = await fetch(`${API_BASE_URL}/submissions/upload-url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("업로드 URL을 생성하지 못했습니다.");
  }

  const data = (await response.json()) as ApiResponse<PresignedUploadResponse>;
  if (!data.data) {
    throw new Error(data.message ?? "업로드 URL 응답이 올바르지 않습니다.");
  }

  return data.data;
}

export async function submitPlatform(payload: SubmissionPayload): Promise<SubmissionResponse> {
  const response = await fetch(`${API_BASE_URL}/submissions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    credentials: "include",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.detail ?? "제출에 실패했습니다.");
  }

  const data = (await response.json()) as ApiResponse<SubmissionResponse>;
  if (!data.data) {
    throw new Error(data.message ?? "제출 응답이 올바르지 않습니다.");
  }

  return data.data;
}

export interface AdminLoginPayload {
  username: string;
  password: string;
}

export interface SubmissionListResponse {
  items: SubmissionResponse[];
  total: number;
}

export async function adminLogin(payload: AdminLoginPayload): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/admin/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    credentials: "include",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.detail ?? "로그인에 실패했습니다.");
  }
}

export async function fetchAdminSubmissions(): Promise<SubmissionListResponse> {
  const response = await fetch(`${API_BASE_URL}/submissions`, {
    credentials: "include",
  });

  if (response.status === 401) {
    throw new Error("UNAUTHORIZED");
  }

  if (!response.ok) {
    throw new Error("제출 목록을 불러오지 못했습니다.");
  }

  const data = (await response.json()) as ApiResponse<SubmissionListResponse>;
  if (!data.data) {
    throw new Error(data.message ?? "제출 목록 응답이 올바르지 않습니다.");
  }

  return data.data;
}

export async function approveSubmission(id: number): Promise<SubmissionResponse> {
  const response = await fetch(`${API_BASE_URL}/submissions/${id}/approve`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.detail ?? "승인에 실패했습니다.");
  }

  const data = (await response.json()) as ApiResponse<SubmissionResponse>;
  if (!data.data) {
    throw new Error(data.message ?? "승인 응답이 올바르지 않습니다.");
  }

  return data.data;
}

export async function rejectSubmission(id: number, reason: string): Promise<SubmissionResponse> {
  const response = await fetch(`${API_BASE_URL}/submissions/${id}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
    credentials: "include",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.detail ?? "거절에 실패했습니다.");
  }

  const data = (await response.json()) as ApiResponse<SubmissionResponse>;
  if (!data.data) {
    throw new Error(data.message ?? "거절 응답이 올바르지 않습니다.");
  }

  return data.data;
}
