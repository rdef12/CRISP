import { useParams } from "react-router-dom";
import { useGetOne, useRecordContext } from "react-admin";
import { ShowAveragedPhoto } from "./ShowAveragedPhoto";
import { useEffect, useState } from "react";
import { ShowSingleCameraResults } from "./ShowSingleCameraResults";
import { ShowSingleCameraAnalysisPlots } from "./ShowSingleCameraAnalysisPlots";

export interface Plot {
  plot_type: string;
  plot_figure: string;
  parameter_labels?: string[];
  parameter_values?: number[];
  parameter_uncertainties?: number[];
  chi_squared?: number;
  number_of_data_points?: number;
  description?: string;
}

export interface SingleCameraAnalyses {
  id: number;
  cameraSettingId: number;
  colourChannel: string;
  averageImage: string;
  beamAngle: number;
  beamAngleUncertainty: number;
  braggPeakPixel: number[];
  braggPeakPixelUncertainty: number[];
  plots: Plot[];
}

interface ShowSingleCameraAnalysesProps {
  refreshTrigger: boolean;
}

export const ShowSingleCameraAnalyses = ({ refreshTrigger }: ShowSingleCameraAnalysesProps) => {
  const [imageUrl, setImageUrl] = useState<string>("");

  const { beamRunId } = useParams();
  const record = useRecordContext();
  const { data: cameraAnalysis, isPending } = useGetOne(
    `camera-analysis/beam-run/${beamRunId}/camera`,
    { 
      id: record?.id,
      meta: { refresh: refreshTrigger }
    }
  );
  useEffect(() => {
    if (cameraAnalysis?.averageImage) {
      setImageUrl(`data:image/jpeg;base64,${cameraAnalysis?.averageImage}`);
    }
  }, [cameraAnalysis]);

  if (isPending) return null;
  
  const hasAllResults = cameraAnalysis?.beamAngle != null && 
                       cameraAnalysis?.beamAngleUncertainty != null && 
                       Array.isArray(cameraAnalysis?.braggPeakPixel) &&
                       cameraAnalysis?.braggPeakPixel != null && 
                       cameraAnalysis?.braggPeakPixelUncertainty != null;
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
      {cameraAnalysis?.plots && (
        <ShowSingleCameraAnalysisPlots plots={cameraAnalysis.plots} />
      )}
    </div>
  )   
}