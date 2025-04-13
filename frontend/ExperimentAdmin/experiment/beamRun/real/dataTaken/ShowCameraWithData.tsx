import { CreateCameraAnalysis } from "./singleCameraAnalysis/CreateCameraAnalysis"
import { ShowRealRunPhoto } from "./singleCameraAnalysis/ShowRealRunPhoto"
import { ShowAnalyses } from "./singleCameraAnalysis/ShowAnalyses"
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
      <ShowAnalyses refreshTrigger={refreshTrigger} />
    </div>
  )
}