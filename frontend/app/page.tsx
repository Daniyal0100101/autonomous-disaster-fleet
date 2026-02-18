import Dashboard from "../components/Dashboard";

export default function Home() {
  return (
    <main className="min-h-screen overflow-x-clip bg-[radial-gradient(circle_at_top,rgba(14,116,144,0.22),transparent_45%),radial-gradient(circle_at_70%_12%,rgba(59,130,246,0.18),transparent_35%),linear-gradient(180deg,#020617_0%,#020617_55%,#0b1020_100%)] text-slate-100">
      <Dashboard />
    </main>
  );
}
