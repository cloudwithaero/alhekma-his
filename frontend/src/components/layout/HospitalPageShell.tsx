import React from "react";
import { ArrowRight } from "lucide-react";
import logoUrl from "@/assets/alhekma-logo.png";

type HospitalPageShellProps = {
  title: string;
  subtitle?: string;
  backPath?: string;
  children: React.ReactNode;
};

export default function HospitalPageShell({
  title,
  subtitle,
  backPath = "/nursing",
  children,
}: HospitalPageShellProps) {
  return (
    <main
      dir="rtl"
      className="min-h-screen bg-slate-50 text-foreground"
    >
      <header className="relative z-20 w-full border-b bg-white shadow-sm">
        <div className="mx-auto grid min-h-[132px] max-w-[1500px] items-center gap-5 px-5 py-5 sm:min-h-[154px] sm:px-8 lg:grid-cols-[1fr_auto_1fr]">
          {/* Left */}
          <div className="order-2 flex items-center justify-start lg:order-1">
            {backPath && (
              <button
                type="button"
                onClick={() =>
                  window.location.replace(backPath)
                }
                className="inline-flex items-center gap-2 rounded-xl border bg-white px-4 py-2 text-sm font-semibold shadow-sm transition hover:bg-slate-50"
              >
                <ArrowRight className="size-4" />
                العودة
              </button>
            )}
          </div>

          {/* Center Logo */}
          <div className="order-1 flex items-center justify-center lg:order-2">
            <img
              src={logoUrl}
              alt="مستشفى الحكمة"
              className="h-[82px] w-full max-w-[300px] object-contain sm:h-[105px] sm:max-w-[360px]"
            />
          </div>

          {/* Right */}
          <div className="order-3 text-center lg:text-right">
            <div className="text-[10px] font-bold tracking-[0.18em] text-emerald-700">
              AL HEKMA HOSPITAL
            </div>

            <h1 className="mt-1 text-2xl font-bold sm:text-3xl">
              {title}
            </h1>

            {subtitle && (
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                {subtitle}
              </p>
            )}
          </div>
        </div>

        <div className="h-px bg-emerald-100" />
      </header>

      {children}
    </main>
  );
}
