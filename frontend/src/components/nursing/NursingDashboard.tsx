import { useEffect, useState } from "react";
import {
  Activity,
  Bell,
  ClipboardCheck,
  FileText,
  HeartPulse,
  LogOut,
  MapPin,
  Pill,
  RefreshCw,
  ShieldCheck,
  UserRound,
  Users,
} from "lucide-react";

import logoUrl from "@/assets/alhekma-logo.png";

type StaffContext = {
  user: string;
  full_name: string;
  employee: string;
  designation?: string | null;
  department?: string | null;
  roles: string[];
  presence: {
    name: string;
    kiosk_device?: string | null;
    kiosk_name?: string | null;
    healthcare_service_unit?: string | null;
    started_at?: string | null;
    status: string;
  };
};

type Patient = {
  inpatient_record: string;
  patient: string;
  patient_name: string;
  gender?: string | null;
  status: string;
  service_unit: string;
  check_in?: string | null;
  admitted_datetime?: string | null;
  expected_discharge?: string | null;
};

type NursingDashboardData = {
  location: string;
  presence: {
    name: string;
    kiosk_device?: string | null;
    healthcare_service_unit?: string | null;
    started_at?: string | null;
    status: string;
  };
  patients: Patient[];
  counts: {
    patients: number;
    tasks: number;
    medications: number;
    alerts: number;
  };
};

function formatTime(value?: string | null) {
  if (!value) {
    return "—";
  }

  try {
    return new Intl.DateTimeFormat("ar-EG", {
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(value));
  } catch {
    return "—";
  }
}

function formatStatus(status: string) {
  switch (status) {
    case "Admitted":
      return "منوم";

    case "Discharge Scheduled":
      return "محدد للخروج";

    case "Discharged":
      return "خرج";

    case "Admission Scheduled":
      return "محدد للدخول";

    case "Cancelled":
      return "ملغى";

    default:
      return status;
  }
}

function StatCard({
  icon,
  label,
  value,
  description,
}: {
  icon: React.ReactNode;
  label: string;
  value: number | string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="text-xs text-muted-foreground">
            {label}
          </div>

          <div className="mt-2 text-3xl font-bold">
            {value}
          </div>
        </div>

        <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
          {icon}
        </div>
      </div>

      <div className="mt-3 text-[11px] leading-5 text-muted-foreground">
        {description}
      </div>
    </div>
  );
}

function ActionCard({
  icon,
  title,
  description,
  onClick,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full rounded-2xl border bg-white p-4 text-right shadow-sm transition hover:-translate-y-0.5 hover:border-emerald-200 hover:bg-emerald-50/30 hover:shadow-md active:translate-y-0"
    >
      <div className="flex items-center gap-3">
        <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
          {icon}
        </div>

        <div className="min-w-0">
          <div className="font-semibold">
            {title}
          </div>

          <div className="mt-1 text-xs leading-5 text-muted-foreground">
            {description}
          </div>
        </div>
      </div>
    </button>
  );
}

function openNursingPage(path: string) {
  window.location.href = path;
}

function openNursingPageNewTab(path: string) {
  window.open(
    path,
    "_blank",
    "noopener,noreferrer",
  );
}

export default function NursingDashboard() {
  const [context, setContext] =
    useState<StaffContext | null>(null);

  const [dashboard, setDashboard] =
    useState<NursingDashboardData | null>(null);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadDashboard(showRefreshing = false) {
    if (showRefreshing) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    setError(null);

    try {
      const [
        contextResponse,
        dashboardResponse,
      ] = await Promise.all([
        fetch(
          "/api/method/alhekma.api.badge_auth.get_current_staff_context",
          {
            method: "GET",
            credentials: "same-origin",
            headers: {
              Accept: "application/json",
            },
          },
        ),

        fetch(
          "/api/method/alhekma.api.nursing.get_dashboard",
          {
            method: "GET",
            credentials: "same-origin",
            headers: {
              Accept: "application/json",
            },
          },
        ),
      ]);

      const contextData =
        await contextResponse.json();

      const dashboardData =
        await dashboardResponse.json();

      if (!contextResponse.ok || !contextData?.message) {
        throw new Error("context_failed");
      }

      if (!dashboardResponse.ok || !dashboardData?.message) {
        const serverMessage =
          dashboardData?.message?.message ||
          dashboardData?.message?.exc_type ||
          "dashboard_failed";

        throw new Error(serverMessage);
      }

      setContext(contextData.message);
      setDashboard(dashboardData.message);
    } catch (err) {
      setContext(null);
      setDashboard(null);

      const reason =
        err instanceof Error
          ? err.message
          : "dashboard_failed";

      if (
        reason.includes(
          "active staff shift presence",
        )
      ) {
        setError(
          "يجب تسجيل الحضور من جهاز الدور الثابت أولًا قبل فتح واجهة التمريض.",
        );
      } else if (reason.includes("Authentication")) {
        setError(
          "جلسة الدخول غير صالحة. سجل الدخول مرة أخرى.",
        );
      } else if (reason.includes("Nursing access")) {
        setError(
          "هذا المستخدم لا يملك صلاحية واجهة التمريض.",
        );
      } else {
        setError(
          "تعذر تحميل بيانات التمريض. تأكد من اتصالك بالنظام الداخلي.",
        );
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    void loadDashboard();
  }, []);

  async function logout() {
    try {
      await fetch("/api/method/logout", {
        method: "GET",
        credentials: "same-origin",
      });
    } finally {
      window.location.replace("/");
    }
  }

  if (loading) {
    return (
      <main
        dir="rtl"
        className="flex min-h-screen items-center justify-center bg-slate-50"
      >
        <div className="flex items-center gap-3 rounded-2xl border bg-white px-5 py-4 shadow-sm">
          <RefreshCw className="size-5 animate-spin text-emerald-700" />

          <span className="text-sm font-medium">
            جاري تحميل واجهة التمريض...
          </span>
        </div>
      </main>
    );
  }

  if (error || !context || !dashboard) {
    return (
      <main
        dir="rtl"
        className="min-h-screen bg-slate-50"
      >

        <div className="flex min-h-[calc(100vh-132px)] items-center justify-center p-6 sm:min-h-[calc(100vh-154px)]">
          <div className="w-full max-w-lg rounded-3xl border bg-white p-7 text-center shadow-lg">
            <div className="mx-auto flex size-14 items-center justify-center rounded-2xl bg-red-50 text-red-600">
              <ShieldCheck className="size-7" />
            </div>

            <h1 className="mt-5 text-2xl font-bold">
              لا يمكن فتح واجهة التمريض
            </h1>

            <p className="mt-3 text-sm leading-7 text-muted-foreground">
              {error ||
                "تعذر التحقق من جلسة الموظف."}
            </p>

            <button
              type="button"
              onClick={() =>
                void loadDashboard()
              }
              className="mt-6 inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-emerald-700 px-5 text-sm font-semibold text-white transition hover:bg-emerald-800"
            >
              <RefreshCw className="size-4" />
              إعادة المحاولة
            </button>
          </div>
        </div>
      </main>
    );
  }

  const patients = dashboard.patients;
  const counts = dashboard.counts;

  return (
    <main
      dir="rtl"
      className="min-h-screen bg-slate-50 text-foreground"
    >

      {/* Dashboard content */}
      <div className="mx-auto max-w-[1500px] px-4 py-5 sm:px-6 lg:px-8 lg:py-7">
        {/* Dashboard header */}
        <section className="mb-5 rounded-3xl border bg-white shadow-sm">
          <div className="grid min-h-[150px] items-center gap-5 px-5 py-6 sm:px-7 lg:grid-cols-[1fr_auto_1fr]">

            {/* Staff */}
            <div className="order-2 flex items-center gap-3 lg:order-1 lg:justify-start">
              <div className="flex size-11 items-center justify-center rounded-full bg-emerald-50 text-emerald-700">
                <UserRound className="size-5" />
              </div>

              <div>
                <div className="text-sm font-semibold">
                  {context.full_name}
                </div>

                <div className="mt-1 text-xs text-muted-foreground">
                  التمريض
                </div>
              </div>

              <button
                type="button"
                onClick={() => void logout()}
                className="mr-2 flex size-10 items-center justify-center rounded-xl border text-muted-foreground transition hover:bg-slate-50 hover:text-red-600"
                title="تسجيل الخروج"
                aria-label="تسجيل الخروج"
              >
                <LogOut className="size-4" />
              </button>
            </div>

            {/* Center logo */}
            <div className="order-1 flex items-center justify-center lg:order-2">
              <img
                src={logoUrl}
                alt="مستشفى الحكمة"
                className="h-[72px] w-[260px] object-contain sm:h-[82px] sm:w-[300px]"
              />
            </div>

            {/* Title */}
            <div className="order-3 text-center lg:text-right">
              <div className="flex items-center justify-center gap-2 text-[10px] font-bold tracking-[0.18em] text-emerald-700 lg:justify-start">
                AL HEKMA HOSPITAL
                <HeartPulse className="size-3.5" />
              </div>

              <h1 className="mt-2 text-2xl font-bold sm:text-3xl">
                لوحة تحكم التمريض
              </h1>

              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                متابعة المرضى والمهام والأدوية داخل نطاق الوحدة الحالية.
              </p>
            </div>

          </div>
        </section>

        {/* Active session / location */}
        <section className="rounded-3xl bg-emerald-800 p-5 text-white shadow-lg sm:p-7">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <div className="flex items-center gap-2 text-xs font-semibold text-emerald-100">
                <span className="size-2 rounded-full bg-emerald-300" />

                SESSION ACTIVE
              </div>

              <h2 className="mt-3 text-2xl font-bold sm:text-3xl">
                أهلاً، {context.full_name}
              </h2>

              <p className="mt-2 text-sm leading-7 text-emerald-100">
                أنت مسجل حاليًا في موقع العمل الخاص بالشيفت.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-2xl border border-white/15 bg-white/10 px-4 py-3">
                <div className="text-[11px] text-emerald-100">
                  الموقع الحالي
                </div>

                <div className="mt-1 flex items-center gap-2 text-sm font-semibold">
                  <MapPin className="size-4 shrink-0" />

                  <span className="line-clamp-2">
                    {dashboard.location}
                  </span>
                </div>
              </div>

              <div className="rounded-2xl border border-white/15 bg-white/10 px-4 py-3">
                <div className="text-[11px] text-emerald-100">
                  الجهاز الثابت
                </div>

                <div className="mt-1 text-sm font-semibold">
                  {context.presence.kiosk_device ||
                    "—"}
                </div>
              </div>

              <div className="rounded-2xl border border-white/15 bg-white/10 px-4 py-3">
                <div className="text-[11px] text-emerald-100">
                  بداية الـPresence
                </div>

                <div className="mt-1 text-sm font-semibold">
                  {formatTime(
                    context.presence.started_at,
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Summary cards */}
        <section className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            icon={<Users className="size-5" />}
            label="المرضى"
            value={counts.patients}
            description="عدد المرضى المنومين داخل نطاق الوحدة الحالية."
          />

          <StatCard
            icon={<ClipboardCheck className="size-5" />}
            label="المهام المفتوحة"
            value={counts.tasks}
            description="مهام التمريض المفتوحة حاليًا."
          />

          <StatCard
            icon={<Pill className="size-5" />}
            label="الأدوية"
            value={counts.medications}
            description="حالة الأدوية المرتبطة بالتمريض."
          />

          <StatCard
            icon={<Bell className="size-5" />}
            label="التنبيهات"
            value={counts.alerts}
            description="التنبيهات التي تحتاج انتباه التمريض."
          />
        </section>

        <div className="mt-5 grid gap-5 xl:grid-cols-[1.65fr_0.9fr]">
          {/* Patients */}
          <section className="overflow-hidden rounded-3xl border bg-white shadow-sm">
            <div className="flex flex-col gap-3 border-b px-5 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
              <div>
                <div className="flex items-center gap-2">
                  <HeartPulse className="size-5 text-emerald-700" />

                  <h2 className="font-bold">
                    المرضى في الوحدة
                  </h2>
                </div>

                <p className="mt-1 text-xs text-muted-foreground">
                  بيانات حقيقية من الـHealthcare Service Unit المرتبطة بالـPresence.
                </p>
              </div>

              <button
                type="button"
                disabled={refreshing}
                onClick={() =>
                  void loadDashboard(true)
                }
                className="inline-flex h-10 items-center justify-center gap-2 rounded-xl border px-3 text-xs font-semibold transition hover:bg-slate-50 disabled:opacity-50"
              >
                <RefreshCw
                  className={
                    refreshing
                      ? "size-4 animate-spin"
                      : "size-4"
                  }
                />

                تحديث
              </button>
            </div>

            <div className="p-5 sm:p-6">
              {patients.length === 0 ? (
                <div className="flex min-h-[260px] items-center justify-center rounded-2xl border border-dashed bg-slate-50/70 p-8 text-center">
                  <div>
                    <div className="mx-auto flex size-14 items-center justify-center rounded-2xl bg-white text-emerald-700 shadow-sm">
                      <Users className="size-6" />
                    </div>

                    <h3 className="mt-4 font-semibold">
                      لا يوجد مرضى حاليًا
                    </h3>

                    <p className="mt-2 text-xs leading-6 text-muted-foreground">
                      لا توجد حالات منومة حاليًا ضمن نطاق الوحدة الحالية.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[720px] text-sm">
                    <thead>
                      <tr className="border-b text-xs text-muted-foreground">
                        <th className="px-3 py-3 text-right font-semibold">
                          المكان
                        </th>

                        <th className="px-3 py-3 text-right font-semibold">
                          المريض
                        </th>

                        <th className="px-3 py-3 text-right font-semibold">
                          الحالة
                        </th>

                        <th className="px-3 py-3 text-right font-semibold">
                          دخول المريض
                        </th>
                      </tr>
                    </thead>

                    <tbody>
                      {patients.map((patient) => (
                        <tr
                          key={patient.inpatient_record}
                          onClick={() =>
                            openNursingPageNewTab(
                              `/nursing/patient/${encodeURIComponent(
                                patient.inpatient_record,
                              )}`,
                            )
                          }
                          className="cursor-pointer border-b transition hover:bg-emerald-50/40 last:border-0"
                          title="فتح ملف الدخول الداخلي"
                        >
                          <td className="px-3 py-4 align-top">
                            <div className="max-w-[240px] font-medium leading-6">
                              {patient.service_unit}
                            </div>
                          </td>

                          <td className="px-3 py-4 align-top">
                            <div className="font-semibold">
                              {patient.patient_name}
                            </div>

                            <div className="mt-1 text-[11px] text-muted-foreground">
                              {patient.patient}
                            </div>
                          </td>

                          <td className="px-3 py-4 align-top">
                            <span className="inline-flex rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                              {formatStatus(
                                patient.status,
                              )}
                            </span>
                          </td>

                          <td className="px-3 py-4 align-top text-xs text-muted-foreground">
                            {formatTime(
                              patient.admitted_datetime,
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </section>

          {/* Nursing actions */}
          <div className="space-y-5">
            <section className="rounded-3xl border bg-white p-5 shadow-sm sm:p-6">
              <div className="flex items-center gap-2">
                <Activity className="size-5 text-emerald-700" />

                <h2 className="font-bold">
                  إجراءات التمريض
                </h2>
              </div>

              <div className="mt-4 space-y-3">
                <ActionCard
                  icon={
                    <HeartPulse className="size-5" />
                  }
                  title="Vital Signs"
                  description="إدخال ومراجعة العلامات الحيوية للمريض."
                  onClick={() =>
                    openNursingPage(
                      "/nursing/vitals",
                    )
                  }
                />

                <ActionCard
                  icon={
                    <FileText className="size-5" />
                  }
                  title="Nursing Note"
                  description="إضافة ملاحظة تمريضية موثقة."
                  onClick={() =>
                    openNursingPage(
                      "/nursing/notes",
                    )
                  }
                />

                <ActionCard
                  icon={
                    <Pill className="size-5" />
                  }
                  title="Medication Administration"
                  description="عرض وتنفيذ الأدوية المستحقة."
                  onClick={() =>
                    openNursingPage(
                      "/nursing/medications",
                    )
                  }
                />

                <ActionCard
                  icon={
                    <ClipboardCheck className="size-5" />
                  }
                  title="Nursing Tasks"
                  description="متابعة المهام التمريضية المفتوحة."
                  onClick={() =>
                    openNursingPage(
                      "/nursing/tasks",
                    )
                  }
                />
              </div>
            </section>

            {/* Shift handover */}
            <section className="rounded-3xl border bg-white p-5 shadow-sm sm:p-6">
              <div className="flex items-center gap-2">
                <FileText className="size-5 text-emerald-700" />

                <h2 className="font-bold">
                  التسليم والاستلام
                </h2>
              </div>

              <div className="mt-4 rounded-2xl border border-dashed bg-slate-50 p-5">
                <div className="text-sm font-semibold">
                  Shift Handover
                </div>

                <p className="mt-2 text-xs leading-6 text-muted-foreground">
                  سيتم ربط تسليم الشيفت بالملاحظات والمهام المفتوحة في مرحلة لاحقة.
                </p>
              </div>
            </section>
          </div>
        </div>
      </div>
    </main>
  );
}
