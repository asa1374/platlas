"use client";

import { useCallback, useRef, useState } from "react";
import dynamic from "next/dynamic";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  requestSubmissionUploadUrl,
  submitPlatform,
  type SubmissionPayload,
} from "@/lib/submissions";

const ReCAPTCHA = dynamic(() => import("react-google-recaptcha"), { ssr: false });

interface FormState extends SubmissionPayload {
  honeypot: string;
}

const initialFormState: FormState = {
  submitter_name: "",
  submitter_email: "",
  platform_name: "",
  description: "",
  website_url: "",
  ios_url: "",
  android_url: "",
  web_url: "",
  screenshot_url: "",
  honeypot: "",
};

export default function SubmitPage() {
  const [form, setForm] = useState<FormState>(initialFormState);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const recaptchaRef = useRef<any>(null);

  const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;

  const handleChange = useCallback(<K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  }, []);

  const resetForm = useCallback(() => {
    setForm(initialFormState);
    setError(null);
    setIsSuccess(false);
    setIsSubmitting(false);
    setIsUploading(false);
  }, []);

  const handleFileChange = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) {
        return;
      }

      setIsUploading(true);
      setError(null);
      try {
        const { uploadUrl, fileUrl } = await requestSubmissionUploadUrl({
          filename: file.name,
          contentType: file.type,
        });

        const uploadResponse = await fetch(uploadUrl, {
          method: "PUT",
          headers: {
            "Content-Type": file.type,
          },
          body: file,
        });

        if (!uploadResponse.ok) {
          throw new Error("파일 업로드에 실패했습니다.");
        }

        handleChange("screenshot_url", fileUrl);
      } catch (uploadError) {
        console.error(uploadError);
        setError(uploadError instanceof Error ? uploadError.message : "파일 업로드 중 오류가 발생했습니다.");
      } finally {
        setIsUploading(false);
      }
    },
    [handleChange]
  );

  const handleSubmit = useCallback(
    async (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();

      if (form.honeypot) {
        return;
      }

      setIsSubmitting(true);
      setError(null);

      try {
        let recaptchaToken: string | undefined;
        if (siteKey && recaptchaRef.current) {
          recaptchaToken = await recaptchaRef.current?.executeAsync?.();
          recaptchaRef.current?.reset?.();
        }

        const payload: SubmissionPayload = {
          submitter_name: form.submitter_name.trim(),
          submitter_email: form.submitter_email.trim(),
          platform_name: form.platform_name.trim(),
          description: form.description?.trim() || undefined,
          website_url: form.website_url?.trim() || undefined,
          ios_url: form.ios_url?.trim() || undefined,
          android_url: form.android_url?.trim() || undefined,
          web_url: form.web_url?.trim() || undefined,
          screenshot_url: form.screenshot_url || undefined,
          recaptchaToken,
        };

        await submitPlatform(payload);
        setIsSuccess(true);
        setForm(initialFormState);
        setIsSubmitting(false);
      } catch (submitError) {
        console.error(submitError);
        setIsSubmitting(false);
        setIsSuccess(false);
        setError(submitError instanceof Error ? submitError.message : "제출 중 오류가 발생했습니다.");
      }
    },
    [form, siteKey]
  );

  if (isSuccess) {
    return (
      <div className="mx-auto flex max-w-2xl flex-col items-center gap-6 py-16">
        <h1 className="text-3xl font-bold">제출이 완료되었습니다!</h1>
        <p className="text-center text-muted-foreground">
          검토 후 이메일로 결과를 알려드릴게요. 소중한 제보에 감사드립니다.
        </p>
        <Button onClick={resetForm}>다른 플랫폼 제출하기</Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl py-12">
      <div className="space-y-4 pb-8 text-center">
        <h1 className="text-3xl font-bold">새로운 플랫폼 제보하기</h1>
        <p className="text-muted-foreground">
          아래 양식을 작성해주시면 운영팀이 빠르게 검토합니다. 가능한 많은 정보를 제공해 주세요.
        </p>
      </div>
      <form className="space-y-6" onSubmit={handleSubmit}>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="submitter_name">이름 *</Label>
            <Input
              id="submitter_name"
              required
              value={form.submitter_name}
              onChange={(event) => handleChange("submitter_name", event.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="submitter_email">이메일 *</Label>
            <Input
              id="submitter_email"
              type="email"
              required
              value={form.submitter_email}
              onChange={(event) => handleChange("submitter_email", event.target.value)}
            />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="platform_name">플랫폼 이름 *</Label>
          <Input
            id="platform_name"
            required
            value={form.platform_name}
            onChange={(event) => handleChange("platform_name", event.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="description">플랫폼 소개</Label>
          <Textarea
            id="description"
            rows={6}
            value={form.description}
            onChange={(event) => handleChange("description", event.target.value)}
            placeholder="플랫폼의 주요 기능, 대상 사용자, 차별점 등을 적어주세요."
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="website_url">공식 웹사이트</Label>
            <Input
              id="website_url"
              type="url"
              value={form.website_url}
              onChange={(event) => handleChange("website_url", event.target.value)}
              placeholder="https://example.com"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="web_url">웹 앱 주소</Label>
            <Input
              id="web_url"
              type="url"
              value={form.web_url}
              onChange={(event) => handleChange("web_url", event.target.value)}
              placeholder="https://app.example.com"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="ios_url">iOS 앱 링크</Label>
            <Input
              id="ios_url"
              type="url"
              value={form.ios_url}
              onChange={(event) => handleChange("ios_url", event.target.value)}
              placeholder="https://apps.apple.com/..."
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="android_url">Android 앱 링크</Label>
            <Input
              id="android_url"
              type="url"
              value={form.android_url}
              onChange={(event) => handleChange("android_url", event.target.value)}
              placeholder="https://play.google.com/..."
            />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="screenshot">스크린샷 (선택)</Label>
          <Input id="screenshot" type="file" accept="image/*" onChange={handleFileChange} />
          {form.screenshot_url ? (
            <p className="text-sm text-muted-foreground">업로드 완료: {form.screenshot_url}</p>
          ) : null}
        </div>
        <div className="hidden">
          <Label htmlFor="honeypot">추가 정보</Label>
          <Input
            id="honeypot"
            autoComplete="off"
            value={form.honeypot}
            onChange={(event) => handleChange("honeypot", event.target.value)}
            tabIndex={-1}
          />
        </div>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        <div className="flex items-center gap-3">
          <Button type="submit" disabled={isSubmitting || isUploading}>
            {isSubmitting ? "제출 중..." : "제출하기"}
          </Button>
          {isUploading ? (
            <span className="text-sm text-muted-foreground">이미지 업로드 중...</span>
          ) : null}
        </div>
        {siteKey ? (
          <ReCAPTCHA
            ref={recaptchaRef}
            sitekey={siteKey}
            size="invisible"
          />
        ) : null}
      </form>
    </div>
  );
}
