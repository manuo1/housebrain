import { useEffect, useState } from "react";
import fetchTeleinfoData from "../services/fetchTeleinfoData";
import TeleinfoData from "../models/TeleinfoData";

interface UseTeleinfoDataResult {
  data: TeleinfoData | null;
  error: string | null;
}

export default function useTeleinfoData(intervalMs = 1000): UseTeleinfoDataResult {
  const [data, setData] = useState<TeleinfoData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchData() {
      try {
        const teleinfoData = await fetchTeleinfoData();
        if (isMounted) {
          setData(teleinfoData);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError((err as Error).message || "Failed to fetch teleinfo data");
        }
      }
    }

    fetchData();
    const interval = setInterval(fetchData, intervalMs);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [intervalMs]);

  return { data, error };
}
