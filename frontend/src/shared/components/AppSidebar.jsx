import { Menu } from "lucide-react";

export default function AppSidebar({
  isOpen,
  onClose,
}) {
  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/30 lg:bg-transparent"
          onClick={onClose}
        />
      )}

      <aside
        className={[
          "fixed inset-y-0 left-0 z-50 w-64 border-r border-slate-200 bg-white shadow-sm transition-transform duration-200",
          isOpen ? "translate-x-0" : "-translate-x-full",
        ].join(" ")}
      >
        <div className="flex h-14 items-center border-b border-slate-200 px-2">
          <div className="flex w-14 shrink-0 items-center justify-center">
            <button
              type="button"
              onClick={onClose}
              className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-slate-300 bg-white text-slate-700 shadow-sm transition hover:bg-slate-50"
              aria-label="Close sidebar"
            >
              <Menu className="h-5 w-5" />
            </button>
          </div>

          <div className="px-2 text-sm font-semibold text-slate-900">
            Menu
          </div>
        </div>

        <nav className="p-4">
          <div className="space-y-1">
            <button
              type="button"
              className="w-full rounded-lg bg-slate-100 px-3 py-2 text-left text-sm font-medium text-slate-900"
            >
              Placeholder
            </button>
          </div>
        </nav>
      </aside>
    </>
  );
}