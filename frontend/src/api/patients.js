import { apiRequest, getAuthHeaders } from "./client";

export function fetchPatients(token) {
  return apiRequest("/api/patients/", {
    headers: {
      ...getAuthHeaders(token),
    },
  });
}

export function createPatient(data, token) {
  return apiRequest("/api/patients/", {
    method: "POST",
    headers: {
      ...getAuthHeaders(token),
    },
    body: JSON.stringify(data),
  });
}

export function updatePatient(id, data, token) {
  return apiRequest(`/api/patients/${id}/`, {
    method: "PUT",
    headers: {
      ...getAuthHeaders(token),
    },
    body: JSON.stringify(data),
  });
}

export function deletePatient(id, token) {
  return apiRequest(`/api/patients/${id}/`, {
    method: "DELETE",
    headers: {
      ...getAuthHeaders(token),
    },
  });
}