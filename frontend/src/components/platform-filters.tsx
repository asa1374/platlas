"use client";

import { useState, useEffect } from "react";
import { FilterIcon, XIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { CategoryRef, TagRef } from "@/lib/api";
import { cn } from "@/lib/utils";

interface PlatformFiltersProps {
  categories: CategoryRef[];
  tags: TagRef[];
  search: string;
  selectedCategoryIds: number[];
  selectedTagIds: number[];
  onSearchChange: (value: string) => void;
  onCategoryToggle: (id: number) => void;
  onTagToggle: (id: number) => void;
  onClear: () => void;
}

export function PlatformFilters({
  categories,
  tags,
  search,
  selectedCategoryIds,
  selectedTagIds,
  onSearchChange,
  onCategoryToggle,
  onTagToggle,
  onClear,
}: PlatformFiltersProps) {
  const [internalSearch, setInternalSearch] = useState(search);

  useEffect(() => {
    setInternalSearch(search);
  }, [search]);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSearchChange(internalSearch.trim());
  };

  const activeFilters = selectedCategoryIds.length + selectedTagIds.length + (search ? 1 : 0);

  return (
    <section className="space-y-6 rounded-2xl border bg-card p-6 shadow-sm">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-lg font-semibold">
          <FilterIcon className="h-5 w-5" />
          탐색 필터
        </div>
        {activeFilters > 0 && (
          <Badge className="bg-primary/15 text-primary">
            활성 필터 {activeFilters}
          </Badge>
        )}
      </header>

      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        <div className="flex flex-col gap-2">
          <Label htmlFor="search">플랫폼 검색</Label>
          <div className="flex flex-col gap-2 sm:flex-row">
            <Input
              id="search"
              placeholder="플랫폼 이름 또는 설명으로 검색"
              value={internalSearch}
              onChange={(event) => setInternalSearch(event.target.value)}
            />
            <div className="flex gap-2">
              <Button type="submit" className="whitespace-nowrap">
                검색
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={() => {
                  setInternalSearch("");
                  onSearchChange("");
                }}
                className={cn("whitespace-nowrap", search ? "visible" : "invisible")}
              >
                지우기
              </Button>
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <FilterGroup
            title="카테고리"
            emptyLabel="등록된 카테고리가 없습니다."
            items={categories}
            selectedIds={selectedCategoryIds}
            onToggle={onCategoryToggle}
          />
          <FilterGroup
            title="태그"
            emptyLabel="등록된 태그가 없습니다."
            items={tags}
            selectedIds={selectedTagIds}
            onToggle={onTagToggle}
          />
        </div>
      </form>

      <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-muted-foreground">
        <p>필터는 TanStack Query를 사용해 즉시 적용되고 캐싱됩니다.</p>
        <Button
          type="button"
          variant="outline"
          onClick={() => {
            setInternalSearch("");
            onClear();
          }}
          className="gap-2 text-xs sm:text-sm"
        >
          <XIcon className="h-4 w-4" /> 필터 초기화
        </Button>
      </div>
    </section>
  );
}

interface FilterGroupProps {
  title: string;
  emptyLabel: string;
  items: Array<{ id: number; name: string }>;
  selectedIds: number[];
  onToggle: (id: number) => void;
}

function FilterGroup({ title, emptyLabel, items, selectedIds, onToggle }: FilterGroupProps) {
  if (items.length === 0) {
    return (
      <div className="rounded-xl border border-dashed bg-muted/20 p-4 text-sm text-muted-foreground">
        {emptyLabel}
      </div>
    );
  }

  return (
    <fieldset className="space-y-3 rounded-xl border bg-background/60 p-4">
      <legend className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
        {title}
      </legend>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {items.map((item) => {
          const checked = selectedIds.includes(item.id);
          return (
            <label
              key={item.id}
              className={cn(
                "flex cursor-pointer items-center gap-3 rounded-lg border px-3 py-2 transition",
                checked ? "border-primary bg-primary/10" : "border-border hover:bg-muted/60"
              )}
            >
              <Checkbox
                checked={checked}
                onCheckedChange={() => onToggle(item.id)}
                aria-label={`${title} ${item.name}`}
              />
              <span className="text-sm font-medium">{item.name}</span>
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}
