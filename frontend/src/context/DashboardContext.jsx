import React, { createContext, useContext, useState, useCallback } from 'react';

const DashboardContext = createContext(null);

export const DashboardProvider = ({ children }) => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const triggerRefresh = useCallback(() => {
    setRefreshTrigger((prev) => prev + 1);
  }, []);

  return (
    <DashboardContext.Provider value={{ refreshTrigger, triggerRefresh }}>
      {children}
    </DashboardContext.Provider>
  );
};

export const useDashboard = () => useContext(DashboardContext);
