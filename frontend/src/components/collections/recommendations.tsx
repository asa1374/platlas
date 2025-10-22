"use client";

import Image from "next/image";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useAnalyticsEvent } from "@/hooks/useAnalyticsEvent";
import type { Collection } from "@/lib/api";

interface CollectionRecommendationsProps {
  collections: Collection[];
}

export function CollectionRecommendations({ collections }: CollectionRecommendationsProps) {
  if (!collections.length) {
    return (
      <div className="rounded-lg border border-dashed p-12 text-center text-muted-foreground">
        표시할 추천 컬렉션이 아직 없습니다.
      </div>
    );
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {collections.map((collection) => (
        <CollectionRecommendationCard key={collection.id} collection={collection} />
      ))}
    </div>
  );
}

function CollectionRecommendationCard({ collection }: { collection: Collection }) {
  const { logClick } = useAnalyticsEvent("collection", collection.id);
  const views = collection.metrics?.views ?? 0;
  const clicks = collection.metrics?.clicks ?? 0;

  return (
    <Card className="flex h-full flex-col overflow-hidden">
      <div className="relative h-40 w-full bg-muted">
        {collection.cover_image_url ? (
          <Image
            alt={`${collection.title} 대표 이미지`}
            src={collection.cover_image_url}
            fill
            sizes="(min-width: 1024px) 33vw, (min-width: 768px) 50vw, 100vw"
            className="object-cover"
            priority={false}
          />
        ) : null}
      </div>
      <CardHeader>
        <CardTitle className="text-lg font-semibold">{collection.title}</CardTitle>
        {collection.highlight ? (
          <p className="text-sm text-muted-foreground">{collection.highlight}</p>
        ) : null}
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-4 text-sm text-muted-foreground">
        {collection.description ? <p>{collection.description}</p> : null}
        <div className="space-y-1 text-xs font-medium uppercase text-muted-foreground">
          <p>포함된 플랫폼 {collection.platforms.length}개</p>
          <p>
            조회수 {views.toLocaleString()} · 클릭 {clicks.toLocaleString()} · 트렌드 지수
            {" "}
            {Math.round(collection.trending_score)}
          </p>
        </div>
      </CardContent>
      <CardFooter className="flex items-center justify-between border-t bg-muted/30 p-4 text-sm">
        <span className="font-medium text-primary">#{collection.platforms[0]?.name ?? "컬렉션"}</span>
        <Button asChild size="sm" onClick={logClick}>
          <Link href={`/collections/${collection.slug}`}>컬렉션 보기</Link>
        </Button>
      </CardFooter>
    </Card>
  );
}
