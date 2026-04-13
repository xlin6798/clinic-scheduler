import { useState } from "react";

export default function usePatientFlow() {
  const [isPatientSearchOpen, setIsPatientSearchOpen] = useState(false);
  const [patientSearchSource, setPatientSearchSource] = useState("appointment");

  const [patientSearchRefreshKey, setPatientSearchRefreshKey] = useState(0);
  const [patientSearchInjectedPatient, setPatientSearchInjectedPatient] =
    useState(null);

  const [isPatientDetailOpen, setIsPatientDetailOpen] = useState(false);
  const [patientDetailMode, setPatientDetailMode] = useState("create");
  const [activePatient, setActivePatient] = useState(null);

  const openCreatePatient = () => {
    setPatientDetailMode("create");
    setActivePatient(null);
    setIsPatientDetailOpen(true);
  };

  const openEditPatient = (patient) => {
    setPatientDetailMode("edit");
    setActivePatient(patient);
    setIsPatientDetailOpen(true);
  };

  const handlePatientSaved = (savedPatient, setSelectedPatient) => {
    setActivePatient(savedPatient);
    setSelectedPatient(savedPatient);
    setPatientSearchInjectedPatient(savedPatient);
    setPatientSearchRefreshKey((prev) => prev + 1);
    setIsPatientDetailOpen(false);
  };

  return {
    isPatientSearchOpen,
    setIsPatientSearchOpen,
    patientSearchSource,
    setPatientSearchSource,
    patientSearchRefreshKey,
    patientSearchInjectedPatient,
    isPatientDetailOpen,
    setIsPatientDetailOpen,
    patientDetailMode,
    activePatient,
    openCreatePatient,
    openEditPatient,
    handlePatientSaved,
  };
}