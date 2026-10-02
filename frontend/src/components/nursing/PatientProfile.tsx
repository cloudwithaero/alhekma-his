import { useEffect, useState } from "react";
import {
  Activity,
  BedDouble,
  CalendarDays,
  Droplets,
  HeartPulse,
  MapPin,
  RefreshCw,
  UserRound,
} from "lucide-react";
import HospitalPageShell from "@/components/layout/HospitalPageShell";

type Patient = {
  patient_name?: string;
  sex?: string;
  dob?: string | null;
  blood_group?: string;
  mobile?: string | null;
  status?: string;
};

type InpatientRecord = {
  name: string;
  patient?: string;
  patient_name?: string;
  status: string;
  admitted_datetime?: string | null;
  discharged_datetime?: string | null;
  expected_discharge?: string | null;
  admission_encounter?: string | null;
};

type Occupancy = {
  name: string;
  service_unit?: string;
  check_in?: string | null;
  check_out?: string | null;
  left?: number;
};

type Location = {
  current_service_unit?: string;
  patient_service_unit?: string;
  kiosk_device?: string;
};

type Vital = {
  name?: string;
  patient?: string;
  patient_name?: string;
  signs_date?: string;
  signs_time?: string;
  temperature?: number | string;
  pulse?: number | string;
  respiratory_rate?: number | string;
  bp_systolic?: number | string;
  bp_diastolic?: number | string;
  oxygen_saturation?: number | string;
  spo2?: number | string;
  weight?: number | string;
  height?: number | string;
  bmi?: number | string;
};

type ProfileData = {
  patient: Patient | null;
  inpatient_record: InpatientRecord;
  occupancy: Occupancy;
  location: Location;
  vital_signs: Vital[];
};

function dash(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  return String(value);
}

function formatDate(value?: string | null) {
  if (!value) return "—";

  try {
    return new Intl.DateTimeFormat("ar-EG", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function systolic(v: Vital) {
  return v.bp_systolic;
}

function diastolic(v: Vital) {
  return v.bp_diastolic;
}

function spo2(v: Vital) {
  return v.spo2;
}

function DataCard({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0">
          <div className="text-xs text-muted-foreground">{label}</div>
          <div className="mt-2 break-words font-semibold">{value}</div>
        </div>

        <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
          {icon}
        </div>
      </div>
    </div>
  );
}

export default function PatientProfile({
  inpatientRecordId,
}: {
  inpatientRecordId: string;
}) {
  const [data, setData] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [savingVital, setSavingVital] = useState(false);
  const [vitalMessage, setVitalMessage] = useState("");
  const [vitalForm, setVitalForm] = useState({
    temperature: "",
    pulse: "",
    respiratory_rate: "",
    bp_systolic: "",
    bp_diastolic: "",
    spo2: "",
    weight: "",
    height: "",
    vital_signs_note: "",
  });

  async function loadProfile() {
    setError("");

    try {
      const response = await fetch(
        `/api/method/alhekma.api.nursing.get_patient_profile?inpatient_record=${encodeURIComponent(
          inpatientRecordId,
        )}`,
        {
          method: "GET",
          credentials: "same-origin",
          headers: {
            Accept: "application/json",
          },
        },
      );

      const result = await response.json();

      if (!response.ok || !result?.message) {
        throw new Error(
          result?.message?.message || "Failed to load patient profile",
        );
      }

      setData(result.message);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "تعذر تحميل بيانات المريض",
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    void loadProfile();
  }, [inpatientRecordId]);

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

  async function recordVitals() {
    setVitalMessage("");

    const values = Object.fromEntries(
      Object.entries(vitalForm).filter(([, value]) => value.trim() !== ""),
    );

    const numericFields = [
      "temperature",
      "pulse",
      "respiratory_rate",
      "bp_systolic",
      "bp_diastolic",
      "spo2",
      "weight",
      "height",
    ];

    if (!numericFields.some((field) => values[field])) {
      setVitalMessage("أدخل علامة حيوية واحدة على الأقل.");
      return;
    }

    setSavingVital(true);

    try {
      const csrfToken = await getCsrfToken();

      const response = await fetch(
        "/api/method/alhekma.api.nursing.record_vital_signs",
        {
          method: "POST",
          credentials: "same-origin",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            "X-Frappe-CSRF-Token": csrfToken,
          },
          body: JSON.stringify({
            inpatient_record: inpatientRecordId,
            ...values,
          }),
        },
      );

      const data = await response.json();

      if (!response.ok || data?.message?.message !== "ok") {
        const message =
          data?.message?.message ||
          data?.message ||
          data?.exception ||
          "تعذر تسجيل العلامات الحيوية.";
        throw new Error(
          typeof message === "string"
            ? message
            : "تعذر تسجيل العلامات الحيوية.",
        );
      }

      setVitalForm({
        temperature: "",
        pulse: "",
        respiratory_rate: "",
        bp_systolic: "",
        bp_diastolic: "",
        spo2: "",
        weight: "",
        height: "",
        vital_signs_note: "",
      });
      setVitalMessage("تم تسجيل العلامات الحيوية واعتماد السجل بنجاح.");
      await loadProfile();
    } catch (err) {
      setVitalMessage(
        err instanceof Error
          ? err.message
          : "تعذر تسجيل العلامات الحيوية.",
      );
    } finally {
      setSavingVital(false);
    }
  }

  function updateVitalField(
    field: keyof typeof vitalForm,
    value: string,
  ) {
    setVitalForm((current) => ({
      ...current,
      [field]: value,
    }));
  }


  if (loading) {
    return (
      <HospitalPageShell title="ملف المريض">
        <div className="flex min-h-[calc(100vh-154px)] items-center justify-center p-6">
          <div className="flex items-center gap-3 rounded-2xl border bg-white px-5 py-4 shadow-sm">
            <RefreshCw className="size-5 animate-spin text-emerald-700" />
            <span>جاري تحميل بيانات المريض...</span>
          </div>
        </div>
      </HospitalPageShell>
    );
  }

  if (error || !data) {
    return (
      <HospitalPageShell
        title="ملف المريض"
        subtitle="تعذر تحميل بيانات المريض"
      >
        <div className="mx-auto max-w-3xl p-6">
          <section className="rounded-3xl border bg-white p-8 shadow-sm">
            <h1 className="text-2xl font-bold">
              تعذر تحميل ملف المريض
            </h1>

            <p className="mt-3 text-sm text-red-600">
              {error || "لا توجد بيانات"}
            </p>

            <button
              type="button"
              onClick={() => void loadProfile()}
              className="mt-6 inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-5 py-3 text-sm font-semibold text-white"
            >
              <RefreshCw className="size-4" />
              إعادة المحاولة
            </button>
          </section>
        </div>
      </HospitalPageShell>
    );
  }

  const patient = data.patient;
  const inpatient = data.inpatient_record;
  const occupancy = data.occupancy;
  const location = data.location;
  const latestVital = data.vital_signs?.[0];

  return (
    <HospitalPageShell
      title="ملف المريض"
      subtitle={patient?.patient_name || "بيانات المريض"}
    >
      <div className="mx-auto max-w-[1400px] px-5 py-6">
        {/* Patient header */}
        <section className="rounded-3xl border bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex size-16 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-700">
                <UserRound className="size-8" />
              </div>

              <div>
                <h2 className="text-2xl font-bold">
                  {dash(patient?.patient_name)}
                </h2>

                <div className="mt-2 text-xs text-muted-foreground">
                  Inpatient Record: {dash(inpatient.name)}
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <span className="rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700">
                {dash(inpatient.status)}
              </span>

              <span className="rounded-full bg-slate-100 px-3 py-1.5 text-xs">
                {dash(patient?.sex)}
              </span>
            </div>
          </div>
        </section>

        {/* Basic information */}
        <section className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <DataCard
            label="الجنس"
            value={dash(patient?.sex)}
            icon={<UserRound className="size-5" />}
          />

          <DataCard
            label="تاريخ الميلاد"
            value={dash(patient?.dob)}
            icon={<CalendarDays className="size-5" />}
          />

          <DataCard
            label="فصيلة الدم"
            value={dash(patient?.blood_group)}
            icon={<Droplets className="size-5" />}
          />

          <DataCard
            label="رقم الهاتف"
            value={dash(patient?.mobile)}
            icon={<Activity className="size-5" />}
          />
        </section>

        {/* Location */}
        <section className="mt-5 rounded-3xl border bg-white p-6 shadow-sm">
          <div className="flex items-center gap-2">
            <MapPin className="size-5 text-emerald-700" />
            <h2 className="font-bold">الموقع الحالي</h2>
          </div>

          <div className="mt-4 grid gap-4 md:grid-cols-3">
            <DataCard
              label="Healthcare Service Unit"
              value={dash(location.current_service_unit)}
              icon={<MapPin className="size-5" />}
            />

            <DataCard
              label="سرير / وحدة المريض"
              value={dash(location.patient_service_unit)}
              icon={<BedDouble className="size-5" />}
            />

            <DataCard
              label="الجهاز الثابت"
              value={dash(location.kiosk_device)}
              icon={<Activity className="size-5" />}
            />
          </div>
        </section>

        {/* Admission */}
        <section className="mt-5 rounded-3xl border bg-white p-6 shadow-sm">
          <h2 className="font-bold">بيانات الدخول</h2>

          <div className="mt-4 grid gap-4 md:grid-cols-3">
            <DataCard
              label="وقت الدخول"
              value={formatDate(inpatient.admitted_datetime)}
              icon={<CalendarDays className="size-5" />}
            />

            <DataCard
              label="Admission Encounter"
              value={dash(inpatient.admission_encounter)}
              icon={<Activity className="size-5" />}
            />

            <DataCard
              label="الخروج المتوقع"
              value={formatDate(inpatient.expected_discharge)}
              icon={<CalendarDays className="size-5" />}
            />
          </div>
        </section>

        {/* Record vital signs */}
        <section className="mt-5 rounded-3xl border bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="font-bold">تسجيل العلامات الحيوية</h2>
              <p className="mt-1 text-xs text-muted-foreground">
                يتم حفظ القراءة باسم المستخدم الحالي ووقت التسجيل من الخادم.
              </p>
            </div>
          </div>

          <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              ["temperature", "الحرارة (°C)", "0.1"],
              ["pulse", "النبض /min", "1"],
              ["respiratory_rate", "معدل التنفس /min", "1"],
              ["bp_systolic", "ضغط انقباضي", "1"],
              ["bp_diastolic", "ضغط انبساطي", "1"],
              ["spo2", "SpO₂ (%)", "0.1"],
              ["weight", "الوزن (kg)", "0.1"],
              ["height", "الطول (m)", "0.01"],
            ].map(([field, label, step]) => (
              <label key={field} className="text-sm">
                <span className="mb-1.5 block font-medium">{label}</span>
                <input
                  type="number"
                  inputMode="decimal"
                  step={step}
                  value={vitalForm[field as keyof typeof vitalForm]}
                  onChange={(event) =>
                    updateVitalField(
                      field as keyof typeof vitalForm,
                      event.target.value,
                    )
                  }
                  className="w-full rounded-xl border bg-white px-3 py-2.5 outline-none focus:border-emerald-600"
                />
              </label>
            ))}
          </div>

          <label className="mt-4 block text-sm">
            <span className="mb-1.5 block font-medium">ملاحظات</span>
            <textarea
              value={vitalForm.vital_signs_note}
              onChange={(event) =>
                updateVitalField("vital_signs_note", event.target.value)
              }
              rows={3}
              className="w-full rounded-xl border bg-white px-3 py-2.5 outline-none focus:border-emerald-600"
            />
          </label>

          <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-xs text-muted-foreground">
              لا توجد حدود أو تنبيهات إكلينيكية مضافة من الواجهة؛ التحقق هنا شكلي فقط بأن القيم رقمية.
            </p>

            <button
              type="button"
              disabled={savingVital}
              onClick={() => void recordVitals()}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-700 px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            >
              {savingVital ? "جاري الحفظ..." : "تسجيل Vital Signs"}
            </button>
          </div>

          {vitalMessage ? (
            <div className="mt-4 rounded-xl border bg-slate-50 px-4 py-3 text-sm">
              {vitalMessage}
            </div>
          ) : null}
        </section>

        {/* Vital signs */}
        <section className="mt-5 rounded-3xl border bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <HeartPulse className="size-5 text-emerald-700" />
              <h2 className="font-bold">أحدث العلامات الحيوية</h2>
            </div>

            <button
              type="button"
              onClick={async () => {
                setRefreshing(true);
                await loadProfile();
              }}
              className="inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-xs font-semibold hover:bg-slate-50"
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

          {!latestVital ? (
            <div className="mt-5 rounded-2xl border border-dashed bg-slate-50 p-8 text-center">
              <HeartPulse className="mx-auto size-8 text-slate-400" />

              <div className="mt-3 font-semibold">
                لا توجد Vital Signs مسجلة
              </div>

              <p className="mt-2 text-xs text-muted-foreground">
                لم يتم تسجيل علامات حيوية لهذا المريض حتى الآن.
              </p>
            </div>
          ) : (
            <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <DataCard
                label="الحرارة"
                value={`${dash(latestVital.temperature)} °C`}
                icon={<Activity className="size-5" />}
              />

              <DataCard
                label="النبض"
                value={`${dash(latestVital.pulse)} /min`}
                icon={<HeartPulse className="size-5" />}
              />

              <DataCard
                label="ضغط الدم"
                value={`${dash(systolic(latestVital))}/${dash(
                  diastolic(latestVital),
                )}`}
                icon={<Activity className="size-5" />}
              />

              <DataCard
                label="SpO₂"
                value={`${dash(spo2(latestVital))}%`}
                icon={<Droplets className="size-5" />}
              />
            </div>
          )}
        </section>

        {/* Record reference */}
        <section className="mt-5 rounded-3xl border bg-white p-6 shadow-sm">
          <div className="text-xs text-muted-foreground">
            Patient Record
          </div>

          <div className="mt-2 break-all font-mono text-sm">
            {inpatient.name}
          </div>

          <div className="mt-2 text-xs text-muted-foreground">
            Occupancy: {dash(occupancy.name)}
          </div>
        </section>
      </div>
    </HospitalPageShell>
  );
}
