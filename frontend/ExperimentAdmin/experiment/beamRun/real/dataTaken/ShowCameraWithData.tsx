import { CreateRangeCalculation } from "./rangeCalculation/CreateRangeCalculation";
import { RangeCalculation } from "./rangeCalculation/RangeCalculation";
import { ShowRange } from "./rangeCalculation/ShowRange";
import { CreateCameraAnalysis } from "./singleCameraAnalysis/CreateCameraAnalysis"
import { ShowAnalyses } from "./singleCameraAnalysis/ShowAnalyses"
import { useState } from "react"

interface ShowCameraWithDataProps {
  onCameraAnalysisCreated: () => void;
  onAnalysisDeleted?: () => void;
}

export const ShowCameraWithData = ({ onCameraAnalysisCreated, onAnalysisDeleted }: ShowCameraWithDataProps) => {
  const [refreshTrigger, setRefreshTrigger] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  const handleAnalysisCreated = () => {
    setRefreshTrigger(prev => !prev);
    setIsCreating(false);
    onCameraAnalysisCreated();
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
      <ShowAnalyses 
        refreshTrigger={refreshTrigger} 
        isCreating={isCreating} 
        onAnalysisDeleted={onAnalysisDeleted}
      />
      <RangeCalculation/>
    </div>
  )
}