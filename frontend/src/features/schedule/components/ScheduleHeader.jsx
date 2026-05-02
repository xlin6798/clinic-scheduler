import { useEffect, useRef, useState } from "react";
import { CalendarDays, ChevronDown, Clock3, Columns3 } from "lucide-react";

import { SLOT_INTERVAL_OPTIONS } from "../utils/scheduleConstants";

const SCHEDULE_MODE_OPTIONS = [
  { value: "resources", label: "Resource", icon: Columns3 },
  { value: "days", label: "Multi-day", icon: CalendarDays },
];

export default function ScheduleHeader({
  facility,
  scheduleMode,
  activeScheduleInterval,
  onScheduleModeChange,
  onScheduleIntervalChange,
}) {
  const [isIntervalExpanded, setIsIntervalExpanded] = useState(false);
  const intervalControlRef = useRef(null);

  useEffect(() => {
    if (!isIntervalExpanded) return undefined;

    const handlePointerDown = (event) => {
      if (intervalControlRef.current?.contains(event.target)) return;
      setIsIntervalExpanded(false);
    };

    const handleKeyDown = (event) => {
      if (event.key === "Escape") setIsIntervalExpanded(false);
    };

    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isIntervalExpanded]);

  return (
    <div className="grid gap-3 border-b border-cf-border bg-cf-surface px-0 py-3 lg:grid-cols-[260px_minmax(0,1fr)] lg:gap-0">
      <div className="min-w-0 px-4 sm:px-5">
        <div className="min-w-0">
          <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-cf-text-subtle">
            Schedule
          </div>
          <div className="truncate text-lg font-semibold tracking-tight text-cf-text">
            {facility?.name || "Schedule"}
          </div>
        </div>
      </div>

      <div className="flex min-w-0 flex-wrap items-center gap-2 px-4 sm:px-5 lg:px-0">
        <div className="inline-flex max-w-full items-center gap-1 rounded-full border border-cf-border bg-cf-surface-muted p-1 text-xs font-semibold shadow-sm">
          {SCHEDULE_MODE_OPTIONS.map(({ value, label, icon: Icon }) => {
            const isActive = scheduleMode === value;

            return (
              <button
                key={value}
                type="button"
                onClick={() => onScheduleModeChange(value)}
                aria-pressed={isActive}
                className={[
                  "inline-flex min-h-8 min-w-[6.75rem] items-center justify-center gap-1.5 rounded-full px-3 transition",
                  isActive
                    ? "bg-cf-text text-cf-page-bg shadow-sm"
                    : "text-cf-text-muted hover:bg-cf-surface hover:text-cf-text",
                ].join(" ")}
              >
                <Icon className="h-3.5 w-3.5" />
                {label}
              </button>
            );
          })}
        </div>

        <div
          ref={intervalControlRef}
          className="relative inline-flex text-xs font-semibold"
          aria-label="Slot interval"
        >
          <button
            type="button"
            onClick={() => setIsIntervalExpanded((current) => !current)}
            aria-expanded={isIntervalExpanded}
            className={[
              "inline-flex min-h-10 items-center gap-2 rounded-full border border-cf-border bg-cf-surface-muted px-3.5 text-cf-text shadow-sm transition",
              isIntervalExpanded
                ? "border-cf-border-strong bg-cf-surface"
                : "hover:border-cf-border-strong hover:bg-cf-surface",
            ].join(" ")}
          >
            <Clock3 className="h-3.5 w-3.5 text-cf-text-subtle" />
            <span className="tabular-nums">{activeScheduleInterval}</span>
            <span className="text-cf-text-muted">min</span>
            <ChevronDown
              className={[
                "h-3.5 w-3.5 text-cf-text-subtle transition-transform",
                isIntervalExpanded ? "rotate-180" : "",
              ].join(" ")}
            />
          </button>

          {isIntervalExpanded ? (
            <div className="absolute left-0 top-[calc(100%+0.4rem)] z-30 grid min-w-full gap-1 rounded-xl border border-cf-border bg-cf-surface p-1.5 shadow-[var(--shadow-panel-lg)]">
              {SLOT_INTERVAL_OPTIONS.map((option) => {
                const isActive = activeScheduleInterval === option;

                return (
                  <button
                    key={option}
                    type="button"
                    onClick={() => {
                      onScheduleIntervalChange(option);
                      setIsIntervalExpanded(false);
                    }}
                    aria-pressed={isActive}
                    className={[
                      "flex min-h-8 items-center justify-between gap-3 rounded-lg px-2.5 text-left transition",
                      isActive
                        ? "bg-cf-text text-cf-page-bg"
                        : "text-cf-text-muted hover:bg-cf-surface-muted hover:text-cf-text",
                    ].join(" ")}
                  >
                    <span className="tabular-nums">{option}</span>
                    <span
                      className={
                        isActive ? "opacity-75" : "text-cf-text-subtle"
                      }
                    >
                      min
                    </span>
                  </button>
                );
              })}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
