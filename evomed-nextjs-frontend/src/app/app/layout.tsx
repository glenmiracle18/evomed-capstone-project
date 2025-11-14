import Link from "next/link";
import { useUser, UserButton } from "@clerk/nextjs";
import { Button } from "~/components/ui/button";

export default function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-[#e9eeea]">
          <header className="border-b border-[#3c4f3d]/10 bg-white">
            <div className="container mx-auto px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-5">
                  <div className="relative">
                    <h1 className="text-xl font-light tracking-wide text-[#3c4f3d]">
                      <span className="font-normal">EvoMed</span>
                    </h1>
                    <div className="absolute -bottom-1 left-0 h-[2px] w-16 bg-[#de8246]"></div>
                  </div>
                  <span className="text-sm font-light text-[#3c4f3d]/70">
                    Variant Analysis
                  </span>

                  <Link href="/app/docs">
                    <Button
                      variant="outline"
                      className="cursor-pointer text-sm font-semibold text-[#3c4f3d]/70"
                      size="sm"
                    >
                      Docs
                    </Button>
                  </Link>
                </div>
                <UserButton />
              </div>
            </div>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
