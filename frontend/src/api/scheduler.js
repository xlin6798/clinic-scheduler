import { apiRequest, getAuthHeaders } from "./client";

export function fetchAppointments({ date, token }) {
  const query = date ? `?date=${encodeURIComponent(date)}` : "";
  return apiRequest(`/api/scheduler/appointments/${query}`, {
    headers: {
      ...getAuthHeaders(token),
    },
  });
}

export function createAppointment(data, token) {
  return apiRequest("/api/scheduler/appointments/", {
    method: "POST",
    headers: {
      ...getAuthHeaders(token),
    },
    body: JSON.stringify(data),
  });
}

export function updateAppointment(id, data, token) {
  return apiRequest(`/api/scheduler/appointments/${id}/`, {
    method: "PUT",
    headers: {
      ...getAuthHeaders(token),
    },
    body: JSON.stringify(data),
  });
}

export function deleteAppointment(id, token) {
  return apiRequest(`/api/scheduler/appointments/${id}/`, {
    method: "DELETE",
    headers: {
      ...getAuthHeaders(token),
    },
  });
}