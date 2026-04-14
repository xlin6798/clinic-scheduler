import { apiRequest, getAuthHeaders } from "../../../shared/api/client";

export function fetchCurrentUser() {
  return apiRequest("/api/facilities/me/", {
    headers: {
      ...getAuthHeaders(),
    },
  });
}

export function fetchPhysicians() {
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
