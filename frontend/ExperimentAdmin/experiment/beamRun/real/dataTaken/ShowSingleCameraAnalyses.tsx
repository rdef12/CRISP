import { useParams } from "react-router-dom";
import { useGetOne, useRecordContext } from "react-admin";
import { ShowAveragedPhoto } from "./ShowAveragedPhoto";
import { useEffect, useState } from "react";
import { ShowSingleCameraResults } from "./ShowSingleCameraResults";

export interface SingleCameraAnalyses {
  id: number;
  cameraSettingId: number;
  colourChannel: string;
  averageImage: string;
  beamAngle: number;
  beamAngleUncertainty: number;
  braggPeakPixel: number[];
  braggPeakPixelUncertainty: number[];
}

export const ShowSingleCameraAnalyses = () => {
  const [imageUrl, setImageUrl] = useState<string>("");

  const { beamRunId } = useParams();
  const record = useRecordContext();
  const { error, isPending, data: cameraAnalysis, refetch } = useGetOne(
    `camera-analysis/beam-run/${beamRunId}/camera`,
    { id: record?.id}
  );
  useEffect(() => {
    if (cameraAnalysis?.averageImage) {
      setImageUrl(`data:image/jpeg;base64,${cameraAnalysis?.averageImage}`);
    }
  }, [cameraAnalysis]);

  if (isPending) return null;
  
  const hasAllResults = cameraAnalysis?.beamAngle !== undefined && 
                       cameraAnalysis?.beamAngleUncertainty !== undefined && 
                       cameraAnalysis?.braggPeakPixel !== undefined && 
                       cameraAnalysis?.braggPeakPixelUncertainty !== undefined;
  console.log("HASSS ALL RESULTDS: ", hasAllResults)
  console.log("Beam Angle", cameraAnalysis.beamAngle)
  console.log("Beam Angle unc", cameraAnalysis.beamAngleUncertainty)
  console.log("peak pos", cameraAnalysis.braggPeakPixel)
  console.log("peak pos unc", cameraAnalysis.braggPeakPixelUncertainty)

  return (
    <div className="space-y-4">
      {cameraAnalysis?.averageImage && cameraAnalysis?.colourChannel && (
        <ShowAveragedPhoto
          imageUrl={imageUrl}
          colourChannel={cameraAnalysis.colourChannel}
        />
      )}
      
      {hasAllResults && (
        <ShowSingleCameraResults
          beamAngle={cameraAnalysis.beamAngle}
          beamAngleUncertainty={cameraAnalysis.beamAngleUncertainty}
          braggPeakPixel={cameraAnalysis.braggPeakPixel}
          braggPeakPixelUncertainty={cameraAnalysis.braggPeakPixelUncertainty}
        />
      )}
    </div>
  )   
}