import { useQuery } from "@tanstack/react-query";
import {
  fetchPhysicians,
  fetchAppointmentStatuses,
  fetchAppointmentTypes,
  fetchPatientGenders,
} from "../api/facilities";

export default function useFacilityConfig(isAuthenticated, facilityId) {
  const enabled = isAuthenticated && !!facilityId;

  const physiciansQuery = useQuery({
    queryKey: ["physicians", facilityId],
    queryFn: fetchPhysicians,
    enabled,
  });

  const statusOptionsQuery = useQuery({
    queryKey: ["appointmentStatuses", facilityId],
    queryFn: fetchAppointmentStatuses,
    enabled,
  });

  const typeOptionsQuery = useQuery({
    queryKey: ["appointmentTypes", facilityId],
    queryFn: fetchAppointmentTypes,
    enabled,
  });

  const genderOptionsQuery = useQuery({
    queryKey: ["patientGenders", facilityId],
    queryFn: fetchPatientGenders,
    enabled,
  });

  return {
    physicians: physiciansQuery.data || [],
    statusOptions: statusOptionsQuery.data || [],
    typeOptions: typeOptionsQuery.data || [],
    genderOptions: genderOptionsQuery.data || [],
  };
}
