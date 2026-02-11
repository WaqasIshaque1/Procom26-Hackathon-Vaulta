import Link from "next/link";
import DashboardLogo from "@/components/ui/DashboardLogo";

export default function Logo() {
  return (
    <Link href="/" className="inline-flex items-center gap-2" aria-label="Vaulta">
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-500">
        <DashboardLogo />
      </div>
      <span className="font-nacelle text-xl font-semibold text-gray-200">Vaulta</span>
    </Link>
  );
}
