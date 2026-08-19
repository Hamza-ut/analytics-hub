import { createContext, useContext, useState, useEffect } from "react";
import { BACKEND_URL } from "../api/config";

const BackendStatusContext = createContext(null);

export function BackendStatusProvider({ children }) {
  const [isBackendDown, setIsBackendDown] = useState(false);

  function markDown() {
    setIsBackendDown(true);
  }

  function markUp() {
    setIsBackendDown(false);
  }

  useEffect(() => {
    // add return if you want to turn off this functionality
    // return;

    const check = async () => {
      try {
        await fetch(`${BACKEND_URL}/health/`);
        markUp();
      } catch {
        markDown();
      }
    };

    check();
    const interval = setInterval(check, 300000); // Check every 5 minutes (300000 ms)
    return () => clearInterval(interval);
  }, []);

  return (
    <BackendStatusContext.Provider value={{ isBackendDown, markDown, markUp }}>
      {children}
    </BackendStatusContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export const useBackendStatus = () => {
  const context = useContext(BackendStatusContext);
  if (!context) {
    throw new Error(
      "useBackendStatus must be used within a BackendStatusProvider",
    );
  }
  return context;
};
