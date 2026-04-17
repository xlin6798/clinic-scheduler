import { apiRequest, getAuthHeaders } from "../../../shared/api/client";

export function fetchPhysicianList() {
  return apiRequest("/api/facilities/physicians/", {
    headers: {
      ...getAuthHeaders(),
    },
  });
}

export function fetchAppointmentStatuses() {
  return apiRequest("/api/facilities/appointment-statuses/", {
    headers: {
      ...getAuthHeaders(),
    },
  });
}

export function fetchAppointmentTypes() {
  return apiRequest("/api/facilities/appointment-types/", {
    headers: {
      ...getAuthHeaders(),
    },
  });
}

export function fetchStaffRoles() {
  return apiRequest("/api/facilities/staff-roles/", {
    headers: {
      ...getAuthHeaders(),
    },
  });
}

export function fetchStaffTitles() {
  return apiRequest("/api/facilities/staff-titles/", {
    headers: {
      ...getAuthHeaders(),
    },
  });
}

export function fetchPatientGenders() {
  return apiRequest("/api/facilities/patient-genders/", {
    headers: {
      ...getAuthHeaders(),
    },
  });
}

export function fetchStaffList() {
  return apiRequest("/api/facilities/staffs/", {
    headers: {
      ...getAuthHeaders(),
    },
  });
}
