import { useGetOne } from "react-admin";
import { ListCamerasInExperimentReal } from "./ListCamerasInExperimentReal";
import { useParams } from "react-router-dom";
import { GlobalBraggPeakDepth } from "./dataTaken/braggPeakDepth/GlobalBraggPeakDepth";
import { CreateRangeCalculation } from "./dataTaken/rangeCalculation/CreateRangeCalculation";
import { ShowMSICData } from "./dataTaken/ShowMSICData";
import { useState } from "react";
import { Breadcrumbs } from "../../../components/Breadcrumbs";

export const ShowRealBeamRun = () => {
  const { beamRunId } = useParams();
  const { data, isPending } = useGetOne( `beam-run/data-taken`, { id: beamRunId } )
  const [cameraAnalysisCreated, setCameraAnalysisCreated] = useState(false);

  if (isPending) return null;
  const dataTaken = data.data_taken
  return (
    
    <div className="space-y-4">
    <Breadcrumbs />
      {dataTaken && (
        <div className="flex gap-4 w-full">
          <div className="flex-1">
            <GlobalBraggPeakDepth cameraAnalysisCreated={cameraAnalysisCreated} />
          </div>
          <div className="flex-1">
            <ShowMSICData />
          </div>
        </div>
      )}
      <ListCamerasInExperimentReal 
        dataTaken={dataTaken} 
        onCameraAnalysisCreated={() => setCameraAnalysisCreated(prev => !prev)}
        onAnalysisDeleted={() => setCameraAnalysisCreated(prev => !prev)}
      />
      {/* {dataTaken && <ComplexAnalysis/>} */}
      {dataTaken && <CreateRangeCalculation />}
    </div>
  );
}