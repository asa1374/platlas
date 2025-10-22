import Link from "next/link";
import { ExternalLinkIcon, Share2Icon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { Platform } from "@/lib/api";

export function PlatformDetail({ platform }: { platform: Platform }) {
  return (
    <article className="space-y-8">
      <header className="space-y-2">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-3xl font-semibold tracking-tight">{platform.name}</h1>
          <span className="rounded-full bg-secondary px-3 py-1 text-xs font-medium uppercase tracking-widest text-secondary-foreground">
            #{platform.slug}
          </span>
        </div>
        {platform.description ? (
          <p className="max-w-3xl text-lg text-muted-foreground">{platform.description}</p>
        ) : (
          <p className="text-muted-foreground">설명이 등록되지 않은 플랫폼입니다.</p>
        )}
      </header>

      <section className="flex flex-wrap gap-3 text-sm text-muted-foreground">
        {platform.url && (
          <Link href={platform.url} target="_blank" className="inline-flex items-center gap-2 rounded-full border px-4 py-2 transition hover:border-primary hover:text-primary">
            <ExternalLinkIcon className="h-4 w-4" /> 공식 홈페이지
          </Link>
        )}
        {platform.links.web && (
          <Link href={platform.links.web} target="_blank" className="inline-flex items-center gap-2 rounded-full border px-4 py-2 transition hover:border-primary hover:text-primary">
            <Share2Icon className="h-4 w-4" /> Web
          </Link>
        )}
        {platform.links.ios && (
          <Link href={platform.links.ios} target="_blank" className="inline-flex items-center gap-2 rounded-full border px-4 py-2 transition hover:border-primary hover:text-primary">
            <Share2Icon className="h-4 w-4" /> iOS
          </Link>
        )}
        {platform.links.android && (
          <Link href={platform.links.android} target="_blank" className="inline-flex items-center gap-2 rounded-full border px-4 py-2 transition hover:border-primary hover:text-primary">
            <Share2Icon className="h-4 w-4" /> Android
          </Link>
        )}
      </section>

      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>카테고리 & 태그</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h2 className="text-sm font-semibold uppercase text-muted-foreground">카테고리</h2>
              <div className="mt-2 flex flex-wrap gap-2">
                {platform.categories.length > 0 ? (
                  platform.categories.map((category) => (
                    <Badge key={`detail-category-${category.id}`} variant="outline">
                      #{category.name}
                    </Badge>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">연결된 카테고리가 없습니다.</p>
                )}
              </div>
            </div>
            <div>
              <h2 className="text-sm font-semibold uppercase text-muted-foreground">태그</h2>
              <div className="mt-2 flex flex-wrap gap-2">
                {platform.tags.length > 0 ? (
                  platform.tags.map((tag) => (
                    <Badge key={`detail-tag-${tag.id}`} className="bg-primary/10 text-primary">
                      {tag.name}
                    </Badge>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">연결된 태그가 없습니다.</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>연관 플랫폼</CardTitle>
          </CardHeader>
          <CardContent>
            {platform.related_platforms.length > 0 ? (
              <ul className="space-y-3 text-sm">
                {platform.related_platforms.map((related) => (
                  <li key={related.id}>
                    <Link href={`/platforms/${related.slug}`} className="flex items-center justify-between rounded-lg border px-3 py-2 transition hover:border-primary hover:text-primary">
                      <span>{related.name}</span>
                      <Share2Icon className="h-4 w-4" />
                    </Link>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted-foreground">연관 플랫폼 정보가 없습니다.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Separator />

      <section className="space-y-4">
        <h2 className="text-lg font-semibold">데이터 요약</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatBlock label="카테고리" value={platform.categories.length.toString()} />
          <StatBlock label="태그" value={platform.tags.length.toString()} />
          <StatBlock label="연관 플랫폼" value={platform.related_platforms.length.toString()} />
          <StatBlock label="링크" value={[platform.url, platform.links.web, platform.links.ios, platform.links.android].filter(Boolean).length.toString()} />
        </div>
      </section>
    </article>
  );
}

function StatBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border bg-card/70 p-4 shadow-sm">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-foreground">{value}</p>
    </div>
  );
}
