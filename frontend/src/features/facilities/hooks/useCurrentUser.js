import { useQuery } from "@tanstack/react-query";
import { fetchCurrentUser } from "../api/facilities";

export default function useCurrentUser(isAuthenticated) {
  const query = useQuery({
    queryKey: ["currentUser"],
    queryFn: fetchCurrentUser,
    enabled: isAuthenticated,
  });

  return {
    ...query,
    currentUser: query.data || null,
    facility: query.data?.facility || null,
    role: query.data?.role || null,
  };
}
