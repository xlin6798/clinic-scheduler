import { formatDOB } from "./dateTime";

export function getAppointmentTimeLabel(appointment, display) {
  const durationLabel = appointment.duration_minutes
    ? `${appointment.duration_minutes}m`
    : "";
  const defaultLabel = [appointment.time, durationLabel]
    .filter(Boolean)
    .join(" · ");

  if (
    !display.showTimeRange ||
    !appointment.time ||
    !appointment.end_time_str
  ) {
    return defaultLabel;
  }

  return `${appointment.time}-${appointment.end_time_str}`;
}

export function getAppointmentDetailText(appointment, display) {
  return [
    display.showVisitType ? appointment.appointment_type_name : "",
    display.showRoom && appointment.room ? `Room ${appointment.room}` : "",
    display.showResource ? appointment.resource_name : "",
    display.showProvider ? appointment.rendering_provider_name : "",
    display.showAppointmentStatus ? appointment.status_name : "",
    display.showDob && appointment.patient_date_of_birth
      ? `DOB ${formatDOB(appointment.patient_date_of_birth)}`
      : "",
    display.showChartNumber && appointment.patient_chart_number
      ? `Chart #${appointment.patient_chart_number}`
      : "",
    display.showReason ? appointment.reason : "",
    display.showNotes ? appointment.notes : "",
  ]
    .filter(Boolean)
    .join(" • ");
}
