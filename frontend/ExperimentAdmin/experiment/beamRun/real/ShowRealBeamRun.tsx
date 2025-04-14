import { useGetOne } from "react-admin";
import { ListCamerasInExperimentReal } from "./ListCamerasInExperimentReal";
import { useParams } from "react-router-dom";
import { GlobalBraggPeakDepth } from "./dataTaken/braggPeakDepth/GlobalBraggPeakDepth";
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
        <div className="grid grid-cols-2 gap-4 w-full">
          <div className="h-full">
            <GlobalBraggPeakDepth 
              cameraAnalysisCreated={cameraAnalysisCreated} 
            />
          </div>
          <div className="h-full">
            <ShowMSICData />
          </div>
        </div>
      )}
      <ListCamerasInExperimentReal 
        dataTaken={dataTaken} 
        onCameraAnalysisCreated={() => setCameraAnalysisCreated(prev => !prev)}
        onAnalysisDeleted={() => setCameraAnalysisCreated(prev => !prev)}
      />
    </div>
  );
}