import type { Metadata } from "next";
import Link from "next/link";
import { ReactNode } from "react";

import "@/app/globals.css";
import { Providers } from "@/app/providers";

export const metadata: Metadata = {
  title: "platlas",
  description: "플랫폼을 탐색하고 비교하는 지식 지도",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-background font-sans antialiased">
        <Providers>
          <div className="flex min-h-screen flex-col">
            <header className="border-b bg-card/60 backdrop-blur">
              <div className="container flex items-center justify-between py-4">
                <Link href="/" className="text-lg font-semibold tracking-tight">
                  platlas
                </Link>
                <span className="text-sm text-muted-foreground">플랫폼 인사이트 허브</span>
              </div>
            </header>
            <main className="flex-1">
              <div className="container py-10">{children}</div>
            </main>
            <footer className="border-t bg-card/80">
              <div className="container py-6 text-sm text-muted-foreground">
                © {new Date().getFullYear()} platlas
              </div>
            </footer>
          </div>
        </Providers>
      </body>
    </html>
  );
}
