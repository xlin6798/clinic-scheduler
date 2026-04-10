import {
  extractStoredDate,
  extractStoredTime,
} from "../../../shared/utils/dateTime";

export default function formatAppointments(appointments, onEditAppointment) {
  return appointments.map((appointment) => ({
    id: appointment.id,
    patient_id: appointment.patient_id,
    patient_name: appointment.patient_name,
    patient_date_of_birth: appointment.patient_date_of_birth,
    patient_chart_number: appointment.patient_chart_number,
    doctor_name: appointment.doctor_name,
    reason: appointment.reason,
    status: appointment.status,
    status_name: appointment.status_name,
    status_code: appointment.status_code,
    status_color: appointment.status_color,
    appointment_type: appointment.appointment_type,
    appointment_type_name: appointment.appointment_type_name,
    appointment_type_code: appointment.appointment_type_code,
    appointment_type_color: appointment.appointment_type_color,
    facility: appointment.facility,
    created_by_name: appointment.created_by_name,
    appointment_time: appointment.appointment_time,
    date: extractStoredDate(appointment.appointment_time),
    time: extractStoredTime(appointment.appointment_time),
    onEdit: () => onEditAppointment(appointment),
  }));
}