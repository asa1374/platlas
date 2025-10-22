"use client";

import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Loader2Icon } from "lucide-react";

import { PlatformFilters } from "@/components/platform-filters";
import { PlatformCard } from "@/components/platform-card";
import { Button } from "@/components/ui/button";
import type { CategoryRef, TagRef } from "@/lib/api";
import { fetchPlatforms } from "@/lib/api";

const PAGE_SIZE = 12;

type FilterState = {
  search: string;
  categories: number[];
  tags: number[];
};

export default function PlatformsPage() {
  const [page, setPage] = useState(1);
  const [{ search, categories, tags }, setFilters] = useState<FilterState>({
    search: "",
    categories: [],
    tags: [],
  });

  const queryResult = useQuery({
    queryKey: ["platforms", { search, categories, tags, page }],
    queryFn: () =>
      fetchPlatforms({
        search: search || undefined,
        categoryIds: categories,
        tagIds: tags,
        page,
        pageSize: PAGE_SIZE,
      }),
    placeholderData: (previousData) => previousData,
    refetchOnMount: true,
    refetchOnReconnect: true,
  });

  const { data, isFetching, isError, error } = queryResult;

  const categoriesFromMeta = useMemo<CategoryRef[]>(
    () => data?.meta?.filters?.categories ?? [],
    [data?.meta?.filters?.categories]
  );
  const tagsFromMeta = useMemo<TagRef[]>(() => data?.meta?.filters?.tags ?? [], [data?.meta?.filters?.tags]);
  const pagination = data?.meta?.pagination;
  const totalPages = pagination?.pages ?? 0;

  useEffect(() => {
    if (totalPages > 0 && page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  const handleSearchChange = (value: string) => {
    setFilters((prev) => ({ ...prev, search: value }));
    setPage(1);
  };

  const handleCategoryToggle = (id: number) => {
    setFilters((prev) => {
      const exists = prev.categories.includes(id);
      const categories = exists ? prev.categories.filter((item) => item !== id) : [...prev.categories, id];
      return { ...prev, categories };
    });
    setPage(1);
  };

  const handleTagToggle = (id: number) => {
    setFilters((prev) => {
      const exists = prev.tags.includes(id);
      const tags = exists ? prev.tags.filter((item) => item !== id) : [...prev.tags, id];
      return { ...prev, tags };
    });
    setPage(1);
  };

  const handleClear = () => {
    setFilters({ search: "", categories: [], tags: [] });
    setPage(1);
  };

  const hasResults = (data?.data?.length ?? 0) > 0;

  return (
    <div className="space-y-8">
      <PlatformFilters
        categories={categoriesFromMeta}
        tags={tagsFromMeta}
        search={search}
        selectedCategoryIds={categories}
        selectedTagIds={tags}
        onSearchChange={handleSearchChange}
        onCategoryToggle={handleCategoryToggle}
        onTagToggle={handleTagToggle}
        onClear={handleClear}
      />

      <section className="space-y-6">
        <header className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-2xl font-semibold">플랫폼 목록</h2>
            {pagination && (
              <p className="text-sm text-muted-foreground">
                총 {pagination.total}개 플랫폼 · {pagination.page}/{Math.max(totalPages, 1)} 페이지
              </p>
            )}
          </div>
          {isFetching && (
            <div className="inline-flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2Icon className="h-4 w-4 animate-spin" /> 데이터 새로고침 중
            </div>
          )}
        </header>

        {isError && (
          <div className="rounded-xl border border-destructive bg-destructive/10 p-6 text-destructive">
            {(error as Error).message}
          </div>
        )}

        {!isError && (
          <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
            {hasResults ? (
              data?.data?.map((platform) => <PlatformCard key={platform.id} platform={platform} />)
            ) : (
              <EmptyState />
            )}
          </div>
        )}

        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-3">
            <Button
              variant="outline"
              disabled={page === 1 || isFetching}
              onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
            >
              이전
            </Button>
            <span className="text-sm text-muted-foreground">
              {page} / {totalPages}
            </span>
            <Button
              variant="outline"
              disabled={page === totalPages || isFetching || totalPages === 0}
              onClick={() => setPage((prev) => prev + 1)}
            >
              다음
            </Button>
          </div>
        )}
      </section>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="col-span-full flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed bg-muted/20 p-10 text-center text-muted-foreground">
      <p className="text-lg font-medium">조건에 맞는 플랫폼이 없습니다.</p>
      <p className="text-sm">검색어나 필터를 조정해 다시 시도해 주세요.</p>
    </div>
  );
}
