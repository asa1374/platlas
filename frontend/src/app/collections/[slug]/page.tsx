import { notFound } from "next/navigation";

import { CollectionDetailView } from "@/components/collections/detail-view";
import { fetchCollectionDetail } from "@/lib/api";

interface CollectionPageProps {
  params: { slug: string };
}

export default async function CollectionPage({ params }: CollectionPageProps) {
  const response = await fetchCollectionDetail(params.slug);
  const collection = response.data;

  if (!collection) {
    notFound();
  }

  return (
    <main className="mx-auto max-w-5xl space-y-12 px-6 py-12">
      <CollectionDetailView collection={collection} />
    </main>
  );
}
