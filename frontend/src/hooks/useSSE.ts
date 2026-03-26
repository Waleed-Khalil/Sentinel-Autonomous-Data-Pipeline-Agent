import { useEffect, useRef, useState } from "react";
import type { SSEAlert } from "../types";

export function useSSE() {
  const [alerts, setAlerts] = useState<SSEAlert[]>([]);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const es = new EventSource("/_/backend/api/v1/stream");
    esRef.current = es;

    es.onmessage = (event) => {
      try {
        const parsed: SSEAlert = JSON.parse(event.data);
        setAlerts((prev) => [parsed, ...prev].slice(0, 50));
      } catch {
        // ignore parse errors
      }
    };

    es.onerror = () => {
      es.close();
      // Reconnect after 5s
      setTimeout(() => {
        esRef.current = new EventSource("/_/backend/api/v1/stream");
      }, 5000);
    };

    return () => es.close();
  }, []);

  return alerts;
}
