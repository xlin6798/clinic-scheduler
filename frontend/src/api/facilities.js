import { apiRequest, getAuthHeaders } from "./client";

export function fetchCurrentUser(token) {
  return apiRequest("/api/facilities/me/", {
    headers: {
      ...getAuthHeaders(token),
    },
  });
}

export function fetchPhysicians(token) {
  return apiRequest("/api/facilities/physicians/", {
    headers: {
      ...getAuthHeaders(token),
    },
  });
}

export function fetchAppointmentStatuses(token) {
  return apiRequest("/api/facilities/appointment-statuses/", {
    headers: {
      ...getAuthHeaders(token),
    },
  });
}

export function fetchAppointmentTypes(token) {
  return apiRequest("/api/facilities/appointment-types/", {
    headers: {
      ...getAuthHeaders(token),
    },
  });
}

export function fetchStaffRoles(token) {
  return apiRequest("/api/facilities/staff-roles/", {
    headers: {
      ...getAuthHeaders(token),
    },
  });
}

export function fetchStaffTitles(token) {
  return apiRequest("/api/facilities/staff-titles/", {
    headers: {
      ...getAuthHeaders(token),
    },
  });
}