import { useQuery } from "@tanstack/react-query";
import { fetchUserProfile } from "../api/accounts";

export default function useCurrentUser(isAuthenticated) {
  const query = useQuery({
    queryKey: ["currentUser"],
    queryFn: fetchUserProfile,
    enabled: isAuthenticated,
  });

  return {
    ...query,
    currentUser: query.data || null,
    facility: query.data?.facility || null,
    role: query.data?.role || null,
  };
}
