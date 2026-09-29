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
  systolic_bp?: number | string;
  diastolic_bp?: number | string;
  systolic_blood_pressure?: number | string;
  diastolic_blood_pressure?: number | string;
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
  return v.systolic_bp ?? v.systolic_blood_pressure;
}

function diastolic(v: Vital) {
  return v.diastolic_bp ?? v.diastolic_blood_pressure;
}

function spo2(v: Vital) {
  return v.oxygen_saturation ?? v.spo2;
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
