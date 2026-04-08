import { apiRequest, getAuthHeaders } from "./client";

export function searchPatients({ search, name, date_of_birth, chart_number } = {}) {
  const params = new URLSearchParams();

  if (search) params.append("search", search);
  if (name) params.append("name", name);
  if (date_of_birth) params.append("date_of_birth", date_of_birth);
  if (chart_number) params.append("chart_number", chart_number);

  const query = params.toString() ? `?${params.toString()}` : "";

  return apiRequest(`/api/patients/${query}`, {
    headers: {
      ...getAuthHeaders(),
    },
  });
}

export function createPatient(data) {
  return apiRequest("/api/patients/", {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });
}

export function updatePatient(id, data) {
  return apiRequest(`/api/patients/${id}/`, {
    method: "PUT",
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });
}

export function deletePatient(id) {
  return apiRequest(`/api/patients/${id}/`, {
    method: "DELETE",
    headers: {
      ...getAuthHeaders(),
    },
  });
}