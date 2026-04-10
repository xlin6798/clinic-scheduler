export default function AppointmentBlock({
  appointment,
  onDoubleClick,
  onDragStart,
}) {
  return (
    <div
      draggable
      className="flex items-center flex-1 min-w-0 h-full cursor-grab rounded-md border border-white px-2"
      style={{
        backgroundColor: appointment.status_color || "#ffffff",
      }}
      onDragStart={(e) => {
        e.stopPropagation();
        onDragStart?.(appointment);
      }}
      onDoubleClick={(e) => {
        e.stopPropagation();
        onDoubleClick();
      }}
    >
      <div
        className="mr-2 shrink-0 rounded-full"
        style={{
          width: "12px",
          height: "12px",
          backgroundColor: appointment.appointment_type_color || "#ccc",
        }}
      />

      <div className="mr-2 min-w-0 truncate text-xs font-semibold text-slate-900">
        {appointment.patient_name}
      </div>

      <div className="min-w-0 flex-1 truncate text-xs text-slate-500">
        {appointment.appointment_type_name || ""}
      </div>
    </div>
  );
}