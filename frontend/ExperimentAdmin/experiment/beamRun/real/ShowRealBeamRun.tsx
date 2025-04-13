import { useGetOne } from "react-admin";
import { ListCamerasInExperimentReal } from "./ListCamerasInExperimentReal";
import { useParams } from "react-router-dom";
import { ShowBraggPeakDepth } from "./dataTaken/ShowBraggPeakDepth";
import { ComplexAnalysis } from "./dataTaken/ComplexAnalysis";
import { EditMSICData } from "./dataTaken/EditMSICData";
import { Button } from "@/components/ui/button";
import { useState } from "react";

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
      {/* {dataTaken && <ShowBraggPeakDepth />} */}
      <ListCamerasInExperimentReal dataTaken={dataTaken} />
      {/* {dataTaken && <ComplexAnalysis/>} */}
    </div>
  );
}