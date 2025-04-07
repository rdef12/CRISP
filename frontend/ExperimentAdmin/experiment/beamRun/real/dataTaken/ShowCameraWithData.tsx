import { CreateCameraAnalysis } from "./CreateCameraAnalysis"
import { ShowRealRunPhoto } from "./ShowRealRunPhoto"
import { ShowSingleCameraAnalyses } from "./ShowSingleCameraAnalyses"
import { useState } from "react"

export const ShowCameraWithData = () => {
  const [refreshTrigger, setRefreshTrigger] = useState(false);

  const handleAnalysisCreated = () => {
    setRefreshTrigger(prev => !prev);
  };

  return (
    <div>
      <CreateCameraAnalysis onAnalysisCreated={handleAnalysisCreated} />
      <ShowRealRunPhoto />
      <ShowSingleCameraAnalyses refreshTrigger={refreshTrigger} />
    </div>
  )
}