import { fetchCollections } from "@/lib/api";
import { CollectionRecommendations } from "@/components/collections/recommendations";

export default async function Home() {
  const response = await fetchCollections({ featured: true, limit: 6 });
  const collections = response.data ?? [];

  return (
    <main className="mx-auto flex max-w-6xl flex-col gap-12 px-6 py-12">
      <section className="space-y-4 text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">이번 주 추천 컬렉션</h1>
        <p className="text-muted-foreground">
          커뮤니티가 주목하는 서비스 컬렉션을 살펴보고 새로운 영감을 얻어보세요.
        </p>
      </section>
      <CollectionRecommendations collections={collections} />
    </main>
  );
}
