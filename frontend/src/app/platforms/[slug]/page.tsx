"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeftIcon, Loader2Icon } from "lucide-react";

import { PlatformDetail } from "@/components/platform-detail";
import { Button } from "@/components/ui/button";
import { fetchPlatformDetail } from "@/lib/api";

export default function PlatformDetailPage() {
  const params = useParams<{ slug: string }>();
  const router = useRouter();
  const slug = params?.slug;

  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ["platform", slug],
    queryFn: async () => {
      if (!slug || Array.isArray(slug)) {
        throw new Error("잘못된 플랫폼 주소입니다.");
      }
      return fetchPlatformDetail(slug);
    },
    enabled: Boolean(slug),
    retry: 1,
  });

  const platform = data?.data;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Button variant="ghost" className="gap-2" onClick={() => router.back()}>
          <ArrowLeftIcon className="h-4 w-4" /> 뒤로
        </Button>
        <Link href="/platforms" className="text-sm text-muted-foreground hover:text-foreground">
          플랫폼 목록으로 돌아가기
        </Link>
      </div>

      {isLoading && (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2Icon className="h-5 w-5 animate-spin" /> 플랫폼 정보를 불러오는 중입니다.
        </div>
      )}

      {isError && (
        <div className="space-y-4 rounded-xl border border-destructive bg-destructive/10 p-8 text-destructive">
          <p>{(error as Error).message}</p>
          <Button variant="outline" onClick={() => refetch()} className="gap-2">
            <Loader2Icon className="h-4 w-4" /> 다시 시도
          </Button>
        </div>
      )}

      {platform && !isError && (
        <div className="space-y-4">
          {isFetching && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2Icon className="h-4 w-4 animate-spin" /> 최신 데이터를 확인하는 중
            </div>
          )}
          <PlatformDetail platform={platform} />
        </div>
      )}
    </div>
  );
}
