import { formatDOB } from "../../../shared/utils/dateTime";

function getMiddleInitial(value) {
  const trimmed = String(value || "").trim();
  if (!trimmed) return "";

  const initial = trimmed.charAt(0).toUpperCase();
  return `${initial}.`;
}

export function getPatientChartName(patient, fallback = "Unknown patient") {
  if (!patient) return fallback;

  const firstName =
    patient.preferred_name ||
    patient.patient_preferred_name ||
    patient.first_name ||
    patient.patient_first_name ||
    "";
  const legalFirstName = patient.first_name || patient.patient_first_name || "";
  const lastName = patient.last_name || patient.patient_last_name || "";
  const middleInitial = getMiddleInitial(
    patient.middle_name || patient.patient_middle_name
  );
  const givenName = [firstName, middleInitial].filter(Boolean).join(" ");
  const chartName = [lastName, givenName].filter(Boolean).join(", ");

  return (
    chartName ||
    [legalFirstName, middleInitial, lastName].filter(Boolean).join(" ") ||
    patient.patient_name ||
    patient.full_name ||
    patient.display_name ||
    fallback
  );
}

export function getPatientFullName(patient, fallback = "Unknown patient") {
  if (!patient) return fallback;

  const firstName = patient.first_name || patient.patient_first_name || "";
  const lastName = patient.last_name || patient.patient_last_name || "";
  const middleInitial = getMiddleInitial(
    patient.middle_name || patient.patient_middle_name
  );

  return (
    [firstName, middleInitial, lastName].filter(Boolean).join(" ") ||
    getPatientChartName(patient, fallback)
  );
}

export function getPatientName(patient, fallback = "Unknown patient") {
  return getPatientChartName(patient, fallback);
}

export function getPatientInitials(patient) {
  return (
    [patient?.first_name, patient?.last_name]
      .map((part) => (part || "").charAt(0))
      .join("")
      .slice(0, 2)
      .toUpperCase() || "PT"
  );
}

export function getPatientDobMrn(patient) {
  return [
    patient?.date_of_birth ? `DOB ${formatDOB(patient.date_of_birth)}` : "",
    patient?.chart_number ? `MRN ${patient.chart_number}` : "",
  ]
    .filter(Boolean)
    .join(" • ");
}
