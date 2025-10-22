"use client";

import Link from "next/link";
import { useCallback } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAnalyticsEvent } from "@/hooks/useAnalyticsEvent";
import { logAnalyticsEvent } from "@/lib/analytics";
import type { Collection } from "@/lib/api";

interface CollectionDetailViewProps {
  collection: Collection;
}

export function CollectionDetailView({ collection }: CollectionDetailViewProps) {
  const { logClick } = useAnalyticsEvent("collection", collection.id);

  const handlePlatformClick = useCallback(
    (platformId: number) => {
      void logAnalyticsEvent({
        entity_type: "platform",
        entity_id: platformId,
        event_type: "click",
        metadata: { source: `collection:${collection.slug}` },
      });
    },
    [collection.slug]
  );

  return (
    <div className="space-y-10">
      <section className="space-y-4 rounded-2xl border bg-card/60 p-8 shadow-sm">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-medium uppercase text-primary/80">Collection</p>
            <h1 className="text-4xl font-bold tracking-tight md:text-5xl">{collection.title}</h1>
          </div>
          <Badge className="self-start md:self-auto">트렌드 지수 {Math.round(collection.trending_score)}</Badge>
        </div>
        {collection.highlight ? <p className="text-lg text-muted-foreground">{collection.highlight}</p> : null}
        {collection.description ? (
          <p className="text-base leading-relaxed text-muted-foreground/90">{collection.description}</p>
        ) : null}
        <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
          <span>조회수 {collection.metrics.views.toLocaleString()}</span>
          <span>클릭 {collection.metrics.clicks.toLocaleString()}</span>
          <span>포함된 플랫폼 {collection.platforms.length}개</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {collection.platforms.slice(0, 3).map((platform) => (
            <Badge key={platform.id} variant="secondary">
              {platform.name}
            </Badge>
          ))}
        </div>
        <div className="flex gap-3">
          <Link
            href="#collection-platforms"
            className="inline-flex items-center rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground shadow hover:bg-primary/90"
            onClick={logClick}
          >
            플랫폼 목록 보기
          </Link>
          <Link
            href="/platforms"
            className="inline-flex items-center rounded-md border px-4 py-2 text-sm font-semibold hover:bg-muted"
          >
            전체 플랫폼 탐색
          </Link>
        </div>
      </section>

      <section id="collection-platforms" className="space-y-4">
        <h2 className="text-2xl font-semibold">포함된 플랫폼</h2>
        {collection.platforms.length === 0 ? (
          <p className="text-muted-foreground">등록된 플랫폼이 없습니다.</p>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {collection.platforms.map((platform) => (
              <Card key={platform.id} className="transition hover:shadow-lg">
                <CardHeader>
                  <CardTitle>
                    <Link
                      href={`/platforms/${platform.slug}`}
                      className="hover:underline"
                      onClick={() => handlePlatformClick(platform.id)}
                    >
                      {platform.name}
                    </Link>
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground">
                  {platform.slug ? (
                    <p>플랫폼 상세에서 더 많은 정보를 확인하세요.</p>
                  ) : (
                    <p>이 플랫폼에 대한 추가 정보가 곧 업데이트됩니다.</p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
