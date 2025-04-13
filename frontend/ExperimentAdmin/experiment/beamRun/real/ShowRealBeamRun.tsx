import { useGetOne } from "react-admin";
import { ListCamerasInExperimentReal } from "./ListCamerasInExperimentReal";
import { useParams } from "react-router-dom";
import { EditMSICData } from "./dataTaken/EditMSICData";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { GlobalBraggPeakDepth } from "./dataTaken/braggPeakDepth/GlobalBraggPeakDepth";

export const ShowRealBeamRun = () => {
  const [showMSICDialog, setShowMSICDialog] = useState(false);
  const { beamRunId } = useParams();
  const { data, isPending } = useGetOne( `beam-run/data-taken`, { id: beamRunId } )
  if (isPending) return null;
  const dataTaken = data.data_taken
  return (
    <div>
      {dataTaken && (
        <div className="mb-4">
          <Button onClick={() => setShowMSICDialog(true)}>
            Edit MSIC Data
          </Button>
          {showMSICDialog && <EditMSICData onClose={() => setShowMSICDialog(false)} />}
        </div>
      )}
      {dataTaken && <GlobalBraggPeakDepth />}
      <ListCamerasInExperimentReal dataTaken={dataTaken} />
      {/* {dataTaken && <ComplexAnalysis/>} */}
    </div>
  );
}