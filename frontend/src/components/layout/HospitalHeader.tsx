import logoUrl from "@/assets/alhekma-logo.png";

export default function HospitalHeader() {
  return (
    <header className="relative z-20 flex min-h-[132px] w-full items-center justify-center border-b bg-white px-5 py-5 shadow-sm sm:min-h-[154px] sm:px-8">
      <div className="absolute inset-x-0 bottom-0 h-px bg-emerald-100" />

      <img
        src={logoUrl}
        alt="مستشفى الحكمة"
        className="h-[82px] w-full max-w-[620px] object-contain sm:h-[105px] sm:max-w-[760px]"
      />
    </header>
  );
}
