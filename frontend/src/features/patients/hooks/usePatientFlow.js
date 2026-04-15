import { useEffect, useState } from "react";
import { fetchPatientById } from "../api/patients";

const RECENT_PATIENTS_KEY = "recentPatients";
const MAX_RECENT_PATIENTS = 10;

export default function usePatientFlow() {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchSource, setSearchSource] = useState("appointment");

  const [searchInjectedPatient, setSearchInjectedPatient] = useState(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState("create");
  const [activePatient, setActivePatient] = useState(null);

  const openModal = ({ mode, patient = null }) => {
    setModalMode(mode);
    setActivePatient(patient);
    setIsModalOpen(true);
  };

  const [recentPatients, setRecentPatients] = useState(() => {
    try {
      const stored = localStorage.getItem(RECENT_PATIENTS_KEY);
      if (!stored) return [];
      const parsed = JSON.parse(stored);
      return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
      console.error("Failed to load recent patients.", error);
      return [];
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(RECENT_PATIENTS_KEY, JSON.stringify(recentPatients));
    } catch (error) {
      console.error("Failed to save recent patients.", error);
    }
  }, [recentPatients]);

  const addRecentPatient = (patient) => {
    if (!patient?.id) return;

    setRecentPatients((prev) => {
      const filtered = prev.filter((item) => item.id !== patient.id);

      return [
        {
          id: patient.id,
          full_name: patient.full_name,
          display_name: patient.display_name,
          date_of_birth: patient.date_of_birth,
          chart_number: patient.chart_number,
        },
        ...filtered,
      ].slice(0, MAX_RECENT_PATIENTS);
    });
  };

  const openPatientFromHistory = async (patient) => {
    if (!patient?.id) return;

    try {
      const fullPatient = await fetchPatientById(patient.id);
      addRecentPatient(patient);
      openModal({ mode: "edit", patient: fullPatient });
    } catch (error) {
      console.error("Failed to load full patient details.", error);
    }
  };

  const closeSearch = () => {
    setIsSearchOpen(false);
  };

  const openSearch = (source) => {
    setSearchSource(source);
    setIsSearchOpen(true);
    setSearchInjectedPatient(null);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setModalMode("create");
    setActivePatient(null);
  };

  const handlePatientSaved = (savedPatient, setSelectedPatient) => {
    setActivePatient(savedPatient);
    setSelectedPatient?.(savedPatient);
    setSearchInjectedPatient(savedPatient);

    if (modalMode === "edit") {
      addRecentPatient(savedPatient);
    }

    closeModal();
  };

  return {
    search: {
      isOpen: isSearchOpen,
      source: searchSource,
      injectedPatient: searchInjectedPatient,
      open: openSearch,
      close: closeSearch,
    },

    modal: {
      isOpen: isModalOpen,
      mode: modalMode,
      patient: activePatient,
      open: openModal,
      close: closeModal,
    },

    recentPatients,
    addRecentPatient,
    handlePatientSaved,
    openPatientFromHistory,
  };
}
