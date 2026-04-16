import { useQuery } from "@tanstack/react-query";
import {
  fetchPhysicianList,
  fetchAppointmentStatuses,
  fetchAppointmentTypes,
  fetchPatientGenders,
  fetchStaffList,
} from "../api/facilities";

export default function useFacilityConfig(isAuthenticated, facilityId) {
  const enabled = isAuthenticated && !!facilityId;

  const physicianListQuery = useQuery({
    queryKey: ["physicians", facilityId],
    queryFn: fetchPhysicianList,
    enabled,
  });

  const staffListQuery = useQuery({
    queryKey: ["staffs", facilityId],
    queryFn: fetchStaffList,
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
    physicians: physicianListQuery.data || [],
    staffs: staffListQuery.data || [],
    statusOptions: statusOptionsQuery.data || [],
    typeOptions: typeOptionsQuery.data || [],
    genderOptions: genderOptionsQuery.data || [],
  };
}
