import Link from "next/link";
import { ExternalLinkIcon, LinkIcon } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Platform } from "@/lib/api";
import { Separator } from "@/components/ui/separator";

export function PlatformCard({ platform }: { platform: Platform }) {
  const { links } = platform;
  const hasLinks = links.ios || links.android || links.web || platform.url;

  return (
    <Card className="flex h-full flex-col">
      <CardHeader className="gap-2">
        <CardTitle className="text-xl">
          <Link href={`/platforms/${platform.slug}`} className="hover:underline">
            {platform.name}
          </Link>
        </CardTitle>
        {platform.description ? (
          <CardDescription>{platform.description}</CardDescription>
        ) : (
          <CardDescription className="italic text-muted-foreground/70">
            설명이 등록되지 않았습니다.
          </CardDescription>
        )}
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-4">
        <div className="flex flex-wrap gap-2">
          {platform.categories.map((category) => (
            <Badge key={`category-${category.id}`} variant="outline">
              #{category.name}
            </Badge>
          ))}
        </div>
        {platform.tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {platform.tags.map((tag) => (
              <Badge key={`tag-${tag.id}`} className="bg-secondary/60">
                {tag.name}
              </Badge>
            ))}
          </div>
        )}
        {platform.related_platforms.length > 0 && (
          <div className="space-y-2 rounded-lg border bg-card/60 p-3">
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              연관 플랫폼
            </p>
            <div className="flex flex-wrap gap-2 text-sm">
              {platform.related_platforms.map((related) => (
                <Link
                  key={`related-${related.id}`}
                  href={`/platforms/${related.slug}`}
                  className="inline-flex items-center gap-1 rounded-md bg-secondary px-2 py-1 text-secondary-foreground transition hover:bg-secondary/80"
                >
                  <LinkIcon className="h-3 w-3" />
                  {related.name}
                </Link>
              ))}
            </div>
          </div>
        )}
      </CardContent>
      {hasLinks && (
        <>
          <Separator className="mx-6 mb-4 mt-auto" />
          <CardFooter className="flex flex-wrap gap-3 text-sm text-muted-foreground">
            {platform.url && (
              <Link href={platform.url} target="_blank" className="inline-flex items-center gap-1 hover:text-foreground">
                <ExternalLinkIcon className="h-4 w-4" />
                공식 홈페이지
              </Link>
            )}
            {links.web && (
              <Link href={links.web} target="_blank" className="inline-flex items-center gap-1 hover:text-foreground">
                <ExternalLinkIcon className="h-4 w-4" />
                Web
              </Link>
            )}
            {links.ios && (
              <Link href={links.ios} target="_blank" className="inline-flex items-center gap-1 hover:text-foreground">
                <ExternalLinkIcon className="h-4 w-4" />
                iOS
              </Link>
            )}
            {links.android && (
              <Link href={links.android} target="_blank" className="inline-flex items-center gap-1 hover:text-foreground">
                <ExternalLinkIcon className="h-4 w-4" />
                Android
              </Link>
            )}
          </CardFooter>
        </>
      )}
    </Card>
  );
}
