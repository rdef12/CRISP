import { createContext, useContext, useState, ReactNode } from 'react';

interface TestDataContextType {
  duration: number;
  setDuration: (duration: number) => void;
}

const TestDataContext = createContext<TestDataContextType | undefined>(undefined);

export function TestDataProvider({ children }: { children: ReactNode }) {
  const [duration, setDuration] = useState(0);

  return (
    <TestDataContext.Provider value={{ duration, setDuration }}>
      {children}
    </TestDataContext.Provider>
  );
}

export function useTestData() {
  const context = useContext(TestDataContext);
  if (context === undefined) {
    throw new Error('useTestData must be used within a TestDataProvider');
  }
  return context;
} 