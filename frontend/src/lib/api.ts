import { API_BASE_URL, type ApiResponse } from "@/lib/utils";

export interface CategoryRef {
  id: number;
  name: string;
}

export interface TagRef {
  id: number;
  name: string;
}

export interface PlatformLinks {
  ios?: string | null;
  android?: string | null;
  web?: string | null;
}

export interface PlatformSummary {
  id: number;
  slug: string;
  name: string;
}

export interface Platform {
  id: number;
  slug: string;
  name: string;
  description?: string | null;
  url?: string | null;
  categories: CategoryRef[];
  tags: TagRef[];
  links: PlatformLinks;
  related_platforms: PlatformSummary[];
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export interface PlatformsMeta {
  pagination: PaginationMeta;
  filters: {
    categories: CategoryRef[];
    tags: TagRef[];
  };
}

export interface PlatformsResponse extends ApiResponse<Platform[]> {
  meta?: PlatformsMeta;
}

export interface PlatformDetailResponse extends ApiResponse<Platform> {}

export interface PlatformListQuery {
  search?: string;
  categoryIds?: number[];
  tagIds?: number[];
  page?: number;
  pageSize?: number;
}

export async function fetchPlatforms(query: PlatformListQuery): Promise<PlatformsResponse> {
  const params = new URLSearchParams();
  if (query.search) {
    params.set("search", query.search);
  }
  query.categoryIds?.forEach((id) => params.append("category_ids", id.toString()));
  query.tagIds?.forEach((id) => params.append("tag_ids", id.toString()));
  if (query.page) {
    params.set("page", query.page.toString());
  }
  if (query.pageSize) {
    params.set("page_size", query.pageSize.toString());
  }

  const queryString = params.toString();
  const response = await fetch(
    `${API_BASE_URL}/platforms${queryString ? `?${queryString}` : ""}`,
    {
      next: { revalidate: 0 }
    }
  );

  if (!response.ok) {
    throw new Error("플랫폼 목록을 불러오지 못했습니다.");
  }

  return (await response.json()) as PlatformsResponse;
}

export async function fetchPlatformDetail(slug: string): Promise<PlatformDetailResponse> {
  const response = await fetch(`${API_BASE_URL}/platforms/${slug}`, {
    next: { revalidate: 0 }
  });

  if (!response.ok) {
    throw new Error("플랫폼 정보를 불러오지 못했습니다.");
  }

  return (await response.json()) as PlatformDetailResponse;
}
