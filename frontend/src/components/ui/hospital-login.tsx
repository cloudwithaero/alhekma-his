import React, { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BadgeCheck,
  Loader2,
  Quote,
  RefreshCw,
  RotateCcw,
  ShieldCheck,
  UserRound,
  X,
} from "lucide-react";

import { Button } from "./button";
import { Input } from "./input";
import { cn } from "@/lib/utils";
import logoUrl from "@/assets/alhekma-logo.png";

type MessageType = "error" | "ok" | "info" | "warning";

interface StatusMessage {
  text: string;
  type: MessageType;
}

interface ArabicQuote {
  text: string;
  source?: string;
}

const FALLBACK_QUOTES: ArabicQuote[] = [
  {
    text: "سلامة المريض تبدأ من دقة كل خطوة يقوم بها الفريق.",
    source: "تذكير للطاقم الطبي",
  },
  {
    text: "الاهتمام بالتفاصيل الصغيرة يصنع فرقًا كبيرًا في جودة الرعاية.",
    source: "تذكير للطاقم الطبي",
  },
  {
    text: "التواصل الواضح بين أفراد الفريق جزء أساسي من الرعاية الآمنة.",
    source: "تذكير للطاقم الطبي",
  },
  {
    text: "كل مريض يحتاج إلى علمٍ دقيق، وقلبٍ حاضر، واحترامٍ كامل.",
    source: "تذكير للطاقم الطبي",
  },
  {
    text: "التعاون بين الفريق الطبي يحول الخبرات الفردية إلى رعاية أكثر أمانًا.",
    source: "تذكير للطاقم الطبي",
  },
];

function extractServerError(data: any): string {
  try {
    if (data?._server_messages) {
      const messages = JSON.parse(data._server_messages);

      if (Array.isArray(messages) && messages.length) {
        const first = JSON.parse(messages[0]);

        if (first?.message) {
          return first.message;
        }
      }
    }
  } catch {
    // Ignore malformed Frappe server messages.
  }

  if (data?.exception?.includes?.("CSRFTokenError")) {
    return "انتهت جلسة الصفحة. أعد تحميل الصفحة وحاول مرة أخرى.";
  }

  if (typeof data?.message === "string") {
    return data.message;
  }

  return "كود الموظف غير صحيح أو غير مسجل في النظام.";
}

const messageStyles: Record<MessageType, string> = {
  error:
    "border-red-200 bg-red-50 text-red-700 dark:border-red-900/40 dark:bg-red-950/30 dark:text-red-200",
  ok:
    "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900/40 dark:bg-emerald-950/30 dark:text-emerald-200",
  info:
    "border-slate-200 bg-slate-50 text-slate-600 dark:border-white/10 dark:bg-white/[0.03] dark:text-white/70",
  warning:
    "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900/40 dark:bg-amber-950/30 dark:text-amber-200",
};

const messageIcons: Record<MessageType, React.ReactNode> = {
  error: <span aria-hidden>⚠️</span>,
  ok: <span aria-hidden>✅</span>,
  info: <span aria-hidden>ℹ️</span>,
  warning: <span aria-hidden>🔔</span>,
};

const KIOSK_DEVICE_ID = "F1-KIOSK-TEST";

export default function HospitalLoginPage() {
  const [badgeCode, setBadgeCode] = useState("");
  const [badgeValid, setBadgeValid] = useState<boolean | null>(null);
  const [loggingIn, setLoggingIn] = useState(false);
  const [message, setMessage] = useState<StatusMessage | null>(null);

  const [quote, setQuote] = useState<ArabicQuote | null>(null);
  const [quoteLoading, setQuoteLoading] = useState(true);
  const [quoteRefreshKey, setQuoteRefreshKey] = useState(0);

  const badgeRef = useRef<HTMLInputElement>(null);

  const busy = loggingIn;

  useEffect(() => {
    const timer = window.setTimeout(() => {
      badgeRef.current?.focus();
    }, 180);

    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    async function loadQuote() {
      setQuoteLoading(true);

      try {
        const response = await fetch(
          `/api/method/alhekma.api.badge_auth.arabic_quote?refresh=${quoteRefreshKey}`,
          {
            method: "GET",
            credentials: "same-origin",
            headers: {
              Accept: "application/json",
            },
            signal: controller.signal,
          },
        );

        if (!response.ok) {
          throw new Error("quote_request_failed");
        }

        const data = await response.json();
        const result = data?.message;

        if (result && typeof result.text === "string" && result.text.trim()) {
          setQuote({
            text: result.text.trim(),
            source:
              typeof result.source === "string" && result.source.trim()
                ? result.source.trim()
                : undefined,
          });
        } else {
          throw new Error("invalid_quote");
        }
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        const fallback =
          FALLBACK_QUOTES[
            Math.floor(Math.random() * FALLBACK_QUOTES.length)
          ];

        setQuote(fallback);
      } finally {
        if (!controller.signal.aborted) {
          setQuoteLoading(false);
        }
      }
    }

    void loadQuote();

    return () => controller.abort();
  }, [quoteRefreshKey]);

  async function getCsrfToken(): Promise<string> {
    const response = await fetch(
      "/api/method/alhekma.api.badge_auth.get_csrf_token",
      {
        method: "GET",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
        },
      },
    );

    const data = await response.json();

    if (!response.ok || !data?.message?.csrf_token) {
      throw new Error("csrf_token_failed");
    }

    return data.message.csrf_token;
  }

  async function login() {
    const code = badgeCode.trim();

    if (!code) {
      setBadgeValid(false);
      setMessage({
        text: "🎫 امسح بطاقة الموظف أو اكتب كود البطاقة أولًا.",
        type: "error",
      });

      badgeRef.current?.focus();
      return;
    }

    if (busy) {
      return;
    }

    setLoggingIn(true);
    setBadgeValid(null);
    setMessage(null);

    try {
      const csrfToken = await getCsrfToken();

      const response = await fetch("/api/method/alhekma.api.badge_auth.kiosk_badge_login", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-Frappe-CSRF-Token": csrfToken,
        },
        body: JSON.stringify({
          badge_code: code,
          kiosk_device: KIOSK_DEVICE_ID,
        }),
      });

      const data = await response.json();

      if (response.ok && data?.message?.message === "ok") {
        setBadgeValid(true);

        setMessage({
          text: "🎉 تم التعرف على البطاقة وتسجيل الدخول بنجاح. جاري فتح النظام...",
          type: "ok",
        });

        window.setTimeout(() => {
const targetPath = "/nursing";
          const targetUrl = `http://alhekma.local:5173${targetPath}`;

          window.location.replace(targetUrl);
        }, 500);

        return;
      }

      setBadgeValid(false);

      setMessage({
        text: extractServerError(data),
        type: "error",
      });

      window.setTimeout(() => {
        badgeRef.current?.focus();
      }, 60);
    } catch (error) {
      setBadgeValid(false);

      setMessage({
        text:
          error instanceof Error && error.message === "csrf_token_failed"
            ? "🔒 تعذر تجهيز جلسة الدخول. أعد تحميل الصفحة وحاول مرة أخرى."
            : "🌐 تعذر الاتصال بخادم المستشفى. تأكد من اتصال الجهاز بالشبكة الداخلية.",
        type: "error",
      });

      window.setTimeout(() => {
        badgeRef.current?.focus();
      }, 60);
    } finally {
      setLoggingIn(false);
    }
  }

  function resetForm() {
    setBadgeCode("");
    setBadgeValid(null);
    setMessage(null);

    window.setTimeout(() => {
      badgeRef.current?.focus();
    }, 80);
  }

  function handleBadgeChange(value: string) {
    setBadgeCode(value);

    if (badgeValid !== null) {
      setBadgeValid(null);
    }

    if (!value) {
      setMessage(null);
    }
  }

  return (
    <main
      dir="rtl"
      className="min-h-screen bg-background text-foreground"
    >
      {/* Full-width upper hospital logo banner */}
      <header className="relative z-20 flex min-h-[132px] w-full items-center justify-center border-b bg-white px-5 py-5 shadow-sm sm:min-h-[154px] sm:px-8">
        <div className="absolute inset-x-0 bottom-0 h-px bg-emerald-100" />

        <img
          src={logoUrl}
          alt="مستشفى الحكمة"
          className="h-[82px] w-full max-w-[620px] object-contain sm:h-[105px] sm:max-w-[760px]"
        />
      </header>

      <div className="relative min-h-[calc(100vh-132px)] overflow-hidden sm:min-h-[calc(100vh-154px)]">
        {/* Calm background */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 overflow-hidden"
        >
          <div className="absolute -right-40 -top-40 size-[480px] rounded-full bg-emerald-500/[0.055] blur-3xl" />
          <div className="absolute -bottom-48 -left-32 size-[460px] rounded-full bg-emerald-700/[0.045] blur-3xl" />

          <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(15,23,42,0.028)_1px,transparent_1px),linear-gradient(to_bottom,rgba(15,23,42,0.028)_1px,transparent_1px)] bg-[size:44px_44px]" />
        </div>

        <div className="relative z-10 grid min-h-[calc(100vh-132px)] lg:grid-cols-[minmax(0,1.08fr)_minmax(440px,.92fr)] sm:min-h-[calc(100vh-154px)]">
          {/* Quote side */}
          <section className="relative hidden overflow-hidden border-l bg-muted/20 px-10 py-12 lg:flex lg:flex-col xl:px-16 xl:py-14">
            <FloatingPaths />

            <div className="relative z-10 mt-auto max-w-2xl pb-4">
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border bg-background/75 px-3 py-1.5 text-xs font-medium text-muted-foreground shadow-sm backdrop-blur">
                <span className="size-1.5 rounded-full bg-emerald-600" />
                اقتباس اليوم
              </div>

              <AnimatePresence mode="wait" initial={false}>
                <motion.div
                  key={quote?.text || (quoteLoading ? "loading" : "fallback")}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.28 }}
                  className="max-w-2xl"
                >
                  <div className="mb-4 flex items-center gap-2 text-emerald-700">
                    <Quote className="size-5" />
                    <span className="text-sm font-semibold">
                      كلمات تلهمنا في رعاية المرضى
                    </span>
                  </div>

                  {quoteLoading ? (
                    <div className="space-y-3">
                      <div className="h-7 w-11/12 animate-pulse rounded-lg bg-muted" />
                      <div className="h-7 w-8/12 animate-pulse rounded-lg bg-muted" />
                      <div className="h-4 w-3/12 animate-pulse rounded bg-muted" />
                    </div>
                  ) : quote ? (
                    <>
                      <blockquote className="text-3xl font-semibold leading-[1.75] tracking-tight text-foreground xl:text-4xl">
                        «{quote.text}»
                      </blockquote>

                      {quote.source && (
                        <p className="mt-5 text-sm text-muted-foreground">
                          — {quote.source}
                        </p>
                      )}
                    </>
                  ) : null}
                </motion.div>
              </AnimatePresence>

              <div className="mt-7 flex items-center gap-3">
                <button
                  type="button"
                  disabled={quoteLoading}
                  onClick={() => setQuoteRefreshKey((value) => value + 1)}
                  className="inline-flex items-center gap-2 rounded-lg border bg-background/70 px-3 py-2 text-xs font-medium text-muted-foreground shadow-sm transition hover:bg-background hover:text-foreground disabled:cursor-wait disabled:opacity-50"
                >
                  <RefreshCw
                    className={cn(
                      "size-3.5",
                      quoteLoading && "animate-spin",
                    )}
                  />
                  اقتباس آخر
                </button>

                <span className="text-[11px] text-muted-foreground">
                  يتغير عند فتح الصفحة أو عند التحديث
                </span>
              </div>
            </div>

            <footer className="relative z-10 mt-auto flex items-center justify-between border-t pt-5 font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
              <span>AL HEKMA HOSPITAL</span>
              <span>STAFF ACCESS</span>
            </footer>
          </section>

          {/* Login side */}
          <section className="flex min-h-full items-center justify-center px-5 py-10 sm:px-8 lg:px-12">
            <div className="w-full max-w-[470px]">
              <div className="mb-9 lg:hidden">
                <div className="mb-4 flex items-center gap-2 text-xs font-semibold text-emerald-700">
                  <span className="size-1.5 rounded-full bg-emerald-600" />
                  اقتباس اليوم
                </div>

                <AnimatePresence mode="wait" initial={false}>
                  <motion.div
                    key={
                      quote?.text ||
                      (quoteLoading ? "loading-mobile" : "fallback-mobile")
                    }
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -5 }}
                    transition={{ duration: 0.24 }}
                    className="rounded-2xl border bg-muted/25 p-4"
                  >
                    {quoteLoading ? (
                      <div className="space-y-2">
                        <div className="h-4 w-11/12 animate-pulse rounded bg-muted" />
                        <div className="h-4 w-7/12 animate-pulse rounded bg-muted" />
                      </div>
                    ) : quote ? (
                      <>
                        <p className="text-sm font-medium leading-7">
                          «{quote.text}»
                        </p>

                        {quote.source && (
                          <p className="mt-2 text-[11px] text-muted-foreground">
                            — {quote.source}
                          </p>
                        )}
                      </>
                    ) : null}
                  </motion.div>
                </AnimatePresence>

                <button
                  type="button"
                  disabled={quoteLoading}
                  onClick={() => setQuoteRefreshKey((value) => value + 1)}
                  className="mt-3 inline-flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground hover:text-foreground disabled:opacity-50"
                >
                  <RefreshCw
                    className={cn(
                      "size-3",
                      quoteLoading && "animate-spin",
                    )}
                  />
                  اقتباس آخر
                </button>
              </div>

              <div className="space-y-3">
                <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700">
                  <span className="size-1.5 rounded-full bg-emerald-600" />
                  STAFF ACCESS · HIS KIOSK
                </div>

                <h1 className="text-3xl font-bold tracking-tight sm:text-[2.15rem]">
                  تسجيل دخول الموظفين
                </h1>

                <p className="max-w-md text-sm leading-7 text-muted-foreground sm:text-[15px]">
                  امسح بطاقة الموظف أو اكتب كود البطاقة ثم اضغط Enter. سيتم تسجيل الدخول تلقائيًا.
                </p>
              </div>

              <div className="mt-7">
                <StepItem
                  active={true}
                  complete={false}
                  icon={<BadgeCheck className="size-4" />}
                  label="بطاقة الموظف"
                  number="01"
                />
              </div>

              <form
                className="mt-7 space-y-6"
                autoComplete="off"
                onSubmit={(event) => {
                  event.preventDefault();
                  void login();
                }}
              >
                <div className="space-y-2.5">
                  <div className="flex items-center justify-between">
                    <label
                      htmlFor="badge-code"
                      className="text-sm font-semibold"
                    >
                      🎫 كود الموظف
                    </label>

                    <span className="font-mono text-[10px] tracking-[0.14em] text-muted-foreground">
                      BADGE ID
                    </span>
                  </div>

                  <div className="relative">
                    <UserRound className="pointer-events-none absolute right-3.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />

                    <Input
                      id="badge-code"
                      ref={badgeRef}
                      autoFocus
                      type="text"
                      inputMode="text"
                      autoCapitalize="characters"
                      autoComplete="off"
                      spellCheck={false}
                      required
                      disabled={busy}
                      value={badgeCode}
                      placeholder="اكتب كود البطاقة ثم اضغط Enter"
                      className={cn(
                        "h-13 rounded-xl bg-background pr-10 pl-10 font-mono text-sm shadow-sm",
                        "transition-[border-color,box-shadow,background-color] duration-200",
                        "focus-visible:ring-4 focus-visible:ring-emerald-600/10",
                        badgeValid === true &&
                          "border-emerald-500/60 bg-emerald-50/30 dark:bg-emerald-950/10",
                        badgeValid === false &&
                          "border-red-400/70 bg-red-50/30 dark:bg-red-950/10",
                      )}
                      onChange={(event) =>
                        handleBadgeChange(event.target.value)
                      }
                      onKeyDown={async (event) => {
                        if (event.key === "Enter") {
                          event.preventDefault();
                          await login();
                        }
                      }}
                    />

                    {badgeCode && !busy && (
                      <button
                        type="button"
                        onClick={() => {
                          setBadgeCode("");
                          setBadgeValid(null);
                          setMessage(null);

                          badgeRef.current?.focus();
                        }}
                        className="absolute left-2.5 top-1/2 flex size-7 -translate-y-1/2 items-center justify-center rounded-md text-muted-foreground transition hover:bg-muted hover:text-foreground"
                        aria-label="مسح كود الموظف"
                        title="مسح"
                      >
                        <X className="size-4" />
                      </button>
                    )}
                  </div>

                  <p className="text-[11px] leading-5 text-muted-foreground">
                    اكتب الكود ثم اضغط Enter، أو استخدم قارئ الـ Barcode / QR لاحقًا.
                  </p>
                </div>

                <Button
                  type="submit"
                  size="lg"
                  disabled={busy}
                  className={cn(
                    "h-13 w-full rounded-xl text-sm font-semibold",
                    "bg-emerald-700 text-white shadow-md shadow-emerald-900/10",
                    "hover:bg-emerald-800",
                    "focus-visible:ring-4 focus-visible:ring-emerald-600/20",
                    "active:translate-y-px",
                  )}
                >
                  {busy ? (
                    <Loader2 className="me-2 size-4 animate-spin" />
                  ) : (
                    <BadgeCheck className="me-2 size-4" />
                  )}

                  <span>
                    {loggingIn ? "جاري تسجيل الدخول..." : "تسجيل الدخول"}
                  </span>
                </Button>

                <AnimatePresence initial={false}>
                  {message && (
                    <motion.div
                      initial={{ opacity: 0, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -4 }}
                      className={cn(
                        "flex items-start gap-2.5 rounded-xl border px-3.5 py-3 text-xs leading-6",
                        messageStyles[message.type],
                      )}
                      role="alert"
                      aria-live="polite"
                    >
                      <span className="mt-0.5 shrink-0">
                        {messageIcons[message.type]}
                      </span>

                      <span>{message.text}</span>
                    </motion.div>
                  )}
                </AnimatePresence>
              </form>

              <div className="mt-7 flex items-center justify-center">
                <button
                  type="button"
                  disabled={busy}
                  onClick={resetForm}
                  className="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs text-muted-foreground transition hover:bg-muted hover:text-foreground disabled:pointer-events-none disabled:opacity-50"
                >
                  <RotateCcw className="size-3.5" />
                  مسح البيانات والبدء من جديد
                </button>
              </div>

              <div className="mt-8 rounded-xl border bg-muted/30 px-4 py-3.5">
                <div className="flex items-start gap-2.5">
                  <ShieldCheck className="mt-0.5 size-4 shrink-0 text-emerald-600" />

                  <p className="text-[11px] leading-6 text-muted-foreground">
                    هذه البوابة مخصصة لموظفي المستشفى المصرح لهم.
                    حافظ على بطاقة الموظف ولا تسمح باستخدامها من شخص آخر.
                  </p>
                </div>
              </div>

              <div className="mt-6 text-center font-mono text-[9px] uppercase tracking-[0.2em] text-muted-foreground/70">
                AL HEKMA HOSPITAL · STAFF ACCESS
              </div>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}

function StepItem({
  active,
  complete,
  icon,
  label,
  number,
}: {
  active: boolean;
  complete: boolean;
  icon: React.ReactNode;
  label: string;
  number: string;
}) {
  return (
    <motion.div
      animate={{
        opacity: active || complete ? 1 : 0.55,
      }}
      className={cn(
        "inline-flex min-w-0 items-center gap-2 rounded-full border px-3 py-1.5",
        "text-xs font-medium transition-colors",
        active
          ? "border-emerald-500/25 bg-emerald-500/[0.07] text-emerald-700"
          : complete
            ? "border-emerald-500/15 bg-emerald-500/[0.04] text-emerald-700"
            : "border-border bg-muted/30 text-muted-foreground",
      )}
    >
      <span className="font-mono text-[9px] opacity-70">{number}</span>
      {icon}
      <span className="truncate">{label}</span>
    </motion.div>
  );
}

function FloatingPaths() {
  const paths = Array.from({ length: 22 }, (_, i) => ({
    id: i,
    d: `M-${340 - i * 5} ${60 + i * 9}
        C-${210 - i * 5} ${10 + i * 3},
        ${70 + i * 6} ${130 + i * 4},
        ${170 + i * 7} ${280 + i * 2}
        C${300 + i * 8} ${470 - i * 3},
        ${520 + i * 7} ${470 - i * 5},
        ${760 + i * 5} ${300 - i * 2}`,
  }));

  return (
    <div className="pointer-events-none absolute inset-0 opacity-35">
      <svg
        viewBox="0 0 760 520"
        className="size-full text-emerald-900/[0.14]"
        preserveAspectRatio="none"
        fill="none"
        aria-hidden="true"
      >
        {paths.map((path) => (
          <motion.path
            key={path.id}
            d={path.d}
            stroke="currentColor"
            strokeWidth={0.55 + path.id * 0.02}
            initial={{
              pathLength: 0.15,
              pathOffset: 0,
              opacity: 0,
            }}
            animate={{
              pathLength: 1,
              pathOffset: [0, 1, 0],
              opacity: [0.08, 0.30, 0.08],
            }}
            transition={{
              duration: 9 + (path.id % 5),
              delay: (path.id % 6) * 0.22,
              repeat: Number.POSITIVE_INFINITY,
              ease: "linear",
            }}
          />
        ))}
      </svg>
    </div>
  );
}
