import { useQuery } from "@tanstack/react-query";
import { fetchAppointments } from "../api/scheduler";

export default function useAppointments(
  isAuthenticated,
  facilityId,
  selectedDate
) {
  const query = useQuery({
    queryKey: ["appointments", selectedDate],
    queryFn: () => fetchAppointments({ date: selectedDate }),
    enabled: isAuthenticated && !!facilityId,
  });

  return {
    ...query,
    appointments: query.data || [],
  };
}
