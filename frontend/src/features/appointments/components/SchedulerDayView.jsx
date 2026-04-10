import { useMemo } from "react";
import { generateTimeSlots } from "../../../shared/utils/timeSlots";
import { getTodayLocal, parseLocalDate } from "../../../shared/utils/dateTime";
import dayjs from "dayjs";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import TextField from "@mui/material/TextField";
import AppointmentBlock from "./AppointmentBlock";

export default function SchedulerDayView({
  appointments,
  intervalMinutes = 15,
  selectedDate,
  onDateChange,
  onSlotDoubleClick,
  onAppointmentDragStart,
  onAppointmentDrop,
}) {
  const timeSlots = useMemo(() => {
    return generateTimeSlots(intervalMinutes);
  }, [intervalMinutes]);

  const changeDay = (offset) => {
    const d = parseLocalDate(selectedDate);
    d.setDate(d.getDate() + offset);

    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");

    onDateChange(`${year}-${month}-${day}`);
  };

  const appointmentsForDay = appointments.filter((a) => a.date === selectedDate);

  return (
    <div className="mt-4">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <button
          type="button"
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          onClick={() => changeDay(-1)}
        >
          Prev
        </button>

        <button
          type="button"
          className="rounded-lg border border-blue-300 bg-white px-3 py-2 text-sm font-medium text-blue-700 transition hover:bg-blue-50"
          onClick={() => onDateChange(getTodayLocal())}
        >
          Today
        </button>

        <button
          type="button"
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          onClick={() => changeDay(1)}
        >
          Next
        </button>

        <DatePicker
          value={selectedDate ? dayjs(selectedDate) : null}
          onChange={(newValue) => {
            if (newValue && newValue.isValid()) {
              onDateChange(newValue.format("YYYY-MM-DD"));
            }
          }}
          slotProps={{
            textField: {
              size: "small",
              sx: { width: 150 },
            },
          }}
        />
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        {timeSlots.map((slot) => {
          const slotAppointments = appointmentsForDay.filter((a) => {
            const [h, m] = a.time.split(":").map(Number);
            const appointmentMinutes = h * 60 + m;

            return (
              appointmentMinutes >= slot.value &&
              appointmentMinutes < slot.value + intervalMinutes
            );
          });

          return (
            <div
              key={slot.value}
              className="flex min-h-[16px] border-b border-slate-200 last:border-b-0"
            >
              <div className="w-[100px] shrink-0 select-none border-r border-slate-200 bg-slate-50 px-2 py-1 text-sm text-slate-600">
                {slot.label}
              </div>

              <div
                className="flex flex-1 gap-1 px-2 cursor-pointer"
                onDoubleClick={() =>
                  onSlotDoubleClick?.(selectedDate, slot.time24)
                }
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  onAppointmentDrop?.(selectedDate, slot.time24);
                }}
              >
                {slotAppointments.map((a) => (
                  <AppointmentBlock
                    key={a.id}
                    appointment={a}
                    onDoubleClick={a.onEdit}
                    onDragStart={onAppointmentDragStart}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}