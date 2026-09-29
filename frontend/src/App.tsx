import HospitalLoginPage from "@/components/ui/hospital-login";
import NursingDashboard from "@/components/nursing/NursingDashboard";
import PatientProfile from "@/components/nursing/PatientProfile";
import HospitalPageShell from "@/components/layout/HospitalPageShell";

function NursingPage({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <HospitalPageShell
      title={title}
      subtitle={subtitle}
    >
      {children}
    </HospitalPageShell>
  );
}

function NursingPlaceholder({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <NursingPage
      title={title}
      subtitle={description}
    >
      <div className="mx-auto max-w-[1400px] px-5 py-6">
        <section className="rounded-3xl border bg-white p-8 shadow-sm">
          <div className="rounded-2xl border border-dashed bg-slate-50 p-10 text-center">
            <div className="text-lg font-semibold">
              الواجهة قيد الربط بالـBackend
            </div>

            <p className="mt-2 text-sm leading-7 text-muted-foreground">
              الصفحة أصبحت داخل واجهة التمريض، وسيتم ربطها
              بالـClinical API الخاص بالنظام.
            </p>
          </div>
        </section>
      </div>
    </NursingPage>
  );
}

function App() {
  const path = window.location.pathname;

  /* Login keeps its own original logo/header */
  if (path === "/") {
    return <HospitalLoginPage />;
  }

  /*
   * Dashboard
   *
   * We keep the dashboard component itself responsible for its
   * dashboard content and staff/session information.
   */
  if (path === "/nursing") {
    return <NursingDashboard />;
  }

  /* Patient profile */
  if (path.startsWith("/nursing/patient/")) {
    const inpatientRecordId = decodeURIComponent(
      path.replace("/nursing/patient/", ""),
    );

    return <PatientProfile inpatientRecordId={inpatientRecordId} />;
  }

  /* Nursing modules */
  if (path === "/nursing/vitals") {
    return (
      <NursingPlaceholder
        title="العلامات الحيوية"
        description="تسجيل ومراجعة Vital Signs للمرضى."
      />
    );
  }

  if (path === "/nursing/notes") {
    return (
      <NursingPlaceholder
        title="ملاحظات التمريض"
        description="إضافة ومراجعة Nursing Notes."
      />
    );
  }

  if (path === "/nursing/medications") {
    return (
      <NursingPlaceholder
        title="إعطاء الأدوية"
        description="متابعة Medication Administration."
      />
    );
  }

  if (path === "/nursing/tasks") {
    return (
      <NursingPlaceholder
        title="مهام التمريض"
        description="عرض ومتابعة مهام التمريض."
      />
    );
  }

  return <HospitalLoginPage />;
}

export default App;
