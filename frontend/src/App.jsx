import "./App.css";
import { useEffect, useState } from "react";
import { login } from "./api/accounts";
import SchedulerDayView from "./components/SchedulerDayView";
import AppointmentFormModal from "./components/AppointmentFormModal";
import LoginForm from "./components/LoginForm";
import PatientSearchModal from "./components/PatientSearchModal";
import PatientDetailModal from "./components/PatientDetailModal";


import {
  getTodayLocal,
  extractStoredDate,
  extractStoredTime,
} from "./utils/dateTime";

import {
  fetchAppointments,
  createAppointment,
  updateAppointment,
  deleteAppointment,
} from "./api/scheduler";

import {
  fetchCurrentUser,
  fetchPhysicians,
  fetchAppointmentStatuses,
  fetchAppointmentTypes,
  fetchPatientGenders,
} from "./api/facilities";

const emptyForm = {
  patient: "",
  doctor_name: "",
  appointment_time: "",
  reason: "",
  status: "",
  appointment_type: "",
  facility: "",
};

function App() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedDate, setSelectedDate] = useState(getTodayLocal());

  const [facility, setFacility] = useState(null);
  const [role, setRole] = useState(null);

  const [physicians, setPhysicians] = useState([]);
  const [statusOptions, setStatusOptions] = useState([]);
  const [typeOptions, setTypeOptions] = useState([]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState(emptyForm);

  const [selectedPatient, setSelectedPatient] = useState(null);
  const [isPatientSearchOpen, setIsPatientSearchOpen] = useState(false);
  const [patientSearchRefreshKey, setPatientSearchRefreshKey] = useState(0);
  const [patientSearchInjectedPatient, setPatientSearchInjectedPatient] = useState(null);

  const [isPatientDetailOpen, setIsPatientDetailOpen] = useState(false);
  const [patientDetailMode, setPatientDetailMode] = useState("create");
  const [activePatient, setActivePatient] = useState(null);
  const [genderOptions, setGenderOptions] = useState([]);

  const [draggedAppointment, setDraggedAppointment] = useState(null);

  const [isAuthenticated, setIsAuthenticated] = useState(
    !!localStorage.getItem("accessToken")
  );
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState("");

  const handleLoginSubmit = async (credentials) => {
    setAuthLoading(true);
    setAuthError("");

    try {
      const data = await login(credentials);

      localStorage.setItem("accessToken", data.access);
      localStorage.setItem("refreshToken", data.refresh);

      setIsAuthenticated(true);
    } catch (err) {
      console.error(err);
      setAuthError("Invalid username or password.");
    } finally {
      setAuthLoading(false);
    }
  };

  const loadGenderOptions = async () => {
    try {
      const data = await fetchPatientGenders();
      setGenderOptions(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load patient genders.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    setIsAuthenticated(false);
    setFacility(null);
    setRole(null);
    setAppointments([]);
    setPhysicians([]);
    setStatusOptions([]);
    setTypeOptions([]);
    setSelectedPatient(null);
    setIsModalOpen(false);
    setEditingId(null);
    setFormData(emptyForm);
    setError("");
  };

  const loadUser = async () => {
    try {
      const data = await fetchCurrentUser();
      setFacility(data.facility || null);
      setRole(data.role || null);
      setError("");
    } catch (err) {
      console.error(err);
      setError("Failed to load user info.");
    }
  };

  const loadPhysicians = async () => {
    try {
      const data = await fetchPhysicians();
      setPhysicians(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load physicians.");
    }
  };

  const loadStatusOptions = async () => {
    try {
      const data = await fetchAppointmentStatuses();
      setStatusOptions(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load appointment statuses.");
    }
  };

  const loadTypeOptions = async () => {
    try {
      const data = await fetchAppointmentTypes();
      setTypeOptions(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load appointment types.");
    }
  };

  const loadAppointments = async (date = selectedDate, silent = false) => {
    try {
      if (!silent) setLoading(true);
      const data = await fetchAppointments({ date });
      setAppointments(data);
      setError("");
    } catch (err) {
      console.error(err);
      setError("Failed to load appointments.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadUser();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated && facility) {
      loadPhysicians();
      loadStatusOptions();
      loadTypeOptions();
      loadGenderOptions();
    }
  }, [isAuthenticated, facility]);

  useEffect(() => {
    if (isAuthenticated && facility) {
      loadAppointments(selectedDate, false);
    }
  }, [isAuthenticated, selectedDate, facility]);

  const openCreateModal = () => {
    setEditingId(null);
    setSelectedPatient(null);
    setFormData({
      ...emptyForm,
      facility: facility?.id || "",
      doctor_name: physicians.length === 1 ? physicians[0].name : "",
      appointment_time: `${selectedDate}T09:00`,
      status: statusOptions.length > 0 ? statusOptions[0].id : "",
      appointment_type: typeOptions.length > 0 ? typeOptions[0].id : "",
    });
    setError("");
    setIsModalOpen(true);
  };

  const openEditModal = (appointment) => {
    setEditingId(appointment.id);

    setSelectedPatient({
      id: appointment.patient_id,
      full_name: appointment.patient_name,
      display_name: appointment.patient_name,
      date_of_birth: appointment.patient_date_of_birth || "",
      chart_number: appointment.patient_chart_number || "",
    });

    setFormData({
      patient: appointment.patient_id,
      doctor_name: appointment.doctor_name,
      appointment_time: appointment.appointment_time.slice(0, 16),
      reason: appointment.reason || "",
      status: appointment.status,
      appointment_type: appointment.appointment_type,
      facility: appointment.facility,
    });

    setError("");
    setIsModalOpen(true);
  };

  const handleSlotDoubleClick = (date, time24) => {
    setEditingId(null);
    setSelectedPatient(null);
    setFormData({
      ...emptyForm,
      facility: facility?.id || "",
      doctor_name: physicians.length === 1 ? physicians[0].name : "",
      appointment_time: `${date}T${time24}`,
      status: statusOptions.length > 0 ? statusOptions[0].id : "",
      appointment_type: typeOptions.length > 0 ? typeOptions[0].id : "",
    });
    setError("");
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingId(null);
    setFormData(emptyForm);
    setSelectedPatient(null);
    setError("");
  };

  const handleSubmit = async (submittedData) => {
    const payload = {
      ...submittedData,
      patient: selectedPatient?.id || "",
      status: submittedData.status ? Number(submittedData.status) : "",
      appointment_type: submittedData.appointment_type
        ? Number(submittedData.appointment_type)
        : "",
      facility: submittedData.facility ? Number(submittedData.facility) : "",
    };

    try {
      if (editingId) {
        await updateAppointment(editingId, payload);
      } else {
        await createAppointment(payload);
      }

      await loadAppointments(selectedDate, true);
      closeModal();
    } catch (err) {
      console.error(err);
      setError("Failed to save appointment.");
    }
  };

  const handleModalDelete = async () => {
    if (!editingId) return;

    if (!window.confirm("Are you sure you want to delete this appointment?")) {
      return;
    }

    try {
      await deleteAppointment(editingId);
      await loadAppointments(selectedDate, true);
      closeModal();
    } catch (err) {
      console.error(err);
      setError("Failed to delete appointment.");
    }
  };

  const handleDragStartAppointment = (appointment) => {
    setDraggedAppointment(appointment);
  };

  const handleDropAppointment = async (date, time24) => {
    if (!draggedAppointment) return;

    const payload = {
      patient: draggedAppointment.patient_id,
      doctor_name: draggedAppointment.doctor_name,
      appointment_time: `${date}T${time24}`,
      reason: draggedAppointment.reason || "",
      status: draggedAppointment.status,
      appointment_type: draggedAppointment.appointment_type,
      facility: draggedAppointment.facility,
    };

    try {
      await updateAppointment(draggedAppointment.id, payload);
      setDraggedAppointment(null);
      await loadAppointments(selectedDate, true);
    } catch (err) {
      console.error(err);
      setError("Failed to move appointment.");
    }
  };

  const formattedAppointments = appointments.map((appointment) => ({
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
    onEdit: () => openEditModal(appointment),
  }));

  if (!isAuthenticated) {
    return (
      <LoginForm
        onSubmit={handleLoginSubmit}
        error={authError}
        loading={authLoading}
      />
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-6">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900">
            {facility?.name || "Facility Scheduler"}
          </h1>
          {role && <p className="mt-1 text-sm text-slate-500">Role: {role}</p>}
        </div>

        <div className="flex items-center gap-3 self-start sm:self-auto">
          <button
            type="button"
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            onClick={openCreateModal}
            disabled={!facility}
          >
            Add Appointment
          </button>

          <button
            type="button"
            onClick={handleLogout}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          >
            Logout
          </button>
        </div>
      </div>

      {error && !isModalOpen && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {(appointments.length > 0 || !loading) && (
        <SchedulerDayView
          appointments={formattedAppointments}
          intervalMinutes={15}
          selectedDate={selectedDate}
          onDateChange={setSelectedDate}
          onSlotDoubleClick={handleSlotDoubleClick}
          onAppointmentDragStart={handleDragStartAppointment}
          onAppointmentDrop={handleDropAppointment}
        />
      )}

      <AppointmentFormModal
        isOpen={isModalOpen}
        mode={editingId ? "edit" : "create"}
        formData={formData}
        physicians={physicians}
        statusOptions={statusOptions}
        typeOptions={typeOptions}
        error={error}
        onSubmit={handleSubmit}
        onClose={closeModal}
        onDelete={handleModalDelete}
        selectedPatient={selectedPatient}
        onSelectPatient={setSelectedPatient}
        onOpenDetailedSearch={() => setIsPatientSearchOpen(true)}
        onOpenCreatePatient={() => {
          setPatientDetailMode("create");
          setActivePatient(null);
          setIsPatientDetailOpen(true);
        }} />

      <PatientSearchModal
        isOpen={isPatientSearchOpen}
        onClose={() => setIsPatientSearchOpen(false)}
        onSelectPatient={(patient) => {
          setSelectedPatient(patient);
          setIsPatientSearchOpen(false);
        }}
        onOpenCreatePatient={() => {
          setPatientDetailMode("create");
          setActivePatient(null);
          setIsPatientDetailOpen(true);
        }}
        onOpenPatientProfile={(patient) => {
          setPatientDetailMode("edit");
          setActivePatient(patient);
          setIsPatientDetailOpen(true);
        }}
        allowSelect={!editingId}
        refreshKey={patientSearchRefreshKey}
        injectedPatient={patientSearchInjectedPatient}
      />

      <PatientDetailModal
        isOpen={isPatientDetailOpen}
        mode={patientDetailMode}
        patient={activePatient}
        genderOptions={genderOptions}
        onClose={() => setIsPatientDetailOpen(false)}
        onSaved={(savedPatient) => {
          setActivePatient(savedPatient);
          setSelectedPatient(savedPatient);
          setPatientSearchInjectedPatient(savedPatient);
          setPatientSearchRefreshKey((prev) => prev + 1);
          setIsPatientDetailOpen(false);
        }}
      />
    </div>
  );
}

export default App;