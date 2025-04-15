import { createContext, useContext, useState, ReactNode } from 'react';

interface RealDataContextType {
  duration: number;
  setDuration: (duration: number) => void;
}

const RealDataContext = createContext<RealDataContextType | undefined>(undefined);

export function RealDataProvider({ children }: { children: ReactNode }) {
  const [duration, setDuration] = useState(0);

  return (
    <RealDataContext.Provider value={{ duration, setDuration }}>
      {children}
    </RealDataContext.Provider>
  );
}

export function useRealData() {
  const context = useContext(RealDataContext);
  if (context === undefined) {
    throw new Error('useRealData must be used within a RealDataProvider');
  }
  return context;
} 