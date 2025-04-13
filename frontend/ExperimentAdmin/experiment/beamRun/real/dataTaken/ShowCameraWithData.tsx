import { CreateCameraAnalysis } from "./singleCameraAnalysis/CreateCameraAnalysis"
import { ShowAnalyses } from "./singleCameraAnalysis/ShowAnalyses"
import { useState } from "react"

export const ShowCameraWithData = () => {
  const [refreshTrigger, setRefreshTrigger] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  const handleAnalysisCreated = () => {
    setRefreshTrigger(prev => !prev);
    setIsCreating(false);
  };

  const handleAnalysisCreating = () => {
    setIsCreating(true);
  };

  return (
    <div className="space-y-4">
      <CreateCameraAnalysis 
        onAnalysisCreated={handleAnalysisCreated} 
        onAnalysisCreating={handleAnalysisCreating}
      />
      <ShowAnalyses refreshTrigger={refreshTrigger} isCreating={isCreating} />
    </div>
  )
}