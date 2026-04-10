import { apiRequest, getAuthHeaders } from "../../../shared/api/client";

export function fetchAppointments({ date } = {}) {
  const query = date ? `?date=${encodeURIComponent(date)}` : "";

  return apiRequest(`/api/scheduler/appointments/${query}`, {
    headers: {
      ...getAuthHeaders(),
    },
  });
}

export function createAppointment(data) {
  return apiRequest("/api/scheduler/appointments/", {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });
}

export function updateAppointment(id, data) {
  return apiRequest(`/api/scheduler/appointments/${id}/`, {
    method: "PUT",
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });
}

export function deleteAppointment(id) {
  return apiRequest(`/api/scheduler/appointments/${id}/`, {
    method: "DELETE",
    headers: {
      ...getAuthHeaders(),
    },
  });
}