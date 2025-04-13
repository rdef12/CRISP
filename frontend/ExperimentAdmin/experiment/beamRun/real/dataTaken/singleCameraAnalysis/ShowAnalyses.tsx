import { useParams } from "react-router-dom";
import { useDelete, useGetOne, useRecordContext } from "react-admin";
import { ShowAveragedPhoto } from "./ShowAveragedPhoto";
import { useEffect, useState } from "react";
import { ShowResults } from "./ShowResults";
import { ShowPlots } from "./ShowPlots";
import { ShowRealRunPhoto } from "./ShowRealRunPhoto";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { RaRecord } from "react-admin";

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

export interface Analyses {
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

interface ShowAnalysesProps {
  refreshTrigger: boolean;
  isCreating: boolean;
}

export const DeleteButton = ({ record, onDelete }: { record: RaRecord | undefined, onDelete: () => void }) => {
  const [deleteOne] = useDelete();
  const { beamRunId } = useParams();
  
  if (!record) return null;

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await deleteOne(
      `camera-analysis/beam-run/${beamRunId}/camera`,
      { id: record.id },
      {
        onSuccess: () => {
          onDelete();
        },
      }
    );
  };

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button 
          variant="destructive" 
          className="w-full"
          onClick={(e) => e.stopPropagation()}
        >
          Delete Analysis
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure you want to delete this analysis?</AlertDialogTitle>
          <AlertDialogDescription>
            This analysis can always be recomputed but may take some time
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={(e) => e.stopPropagation()}>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

export const ShowAnalyses = ({ refreshTrigger, isCreating }: ShowAnalysesProps) => {
  const [imageUrl, setImageUrl] = useState<string>("");
  const [showPlotsDialog, setShowPlotsDialog] = useState(false);

  const { beamRunId } = useParams();
  const record = useRecordContext();
  const { data: cameraAnalysis, isPending, refetch } = useGetOne(
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

  if (isPending || isCreating) return (
    <div className="space-y-4">
      <div className="w-full">
        <table className="w-full text-sm">
          <tbody>
            <tr>
              <td className="px-4 py-2">
                <strong>Camera Username:</strong> {record?.username}
              </td>
              <td className="px-4 py-2">
                <strong>IP Address:</strong> {record?.ip_address}
              </td>
              <td className="px-4 py-2">
                <strong>Camera ID:</strong> {record?.id}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1">
          <ShowRealRunPhoto />
        </div>
        <div className="flex-1">
          <div className="h-full flex items-center justify-center">
            <div style={{ 
              width: '150px',
              height: '150px',
              border: '4px solid #E5E7EB',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              borderTopColor: '#4B5563',
              borderRightColor: 'transparent',
              borderBottomColor: 'transparent',
              borderLeftColor: 'transparent'
            }}></div>
            <style jsx>{`
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
            `}</style>
          </div>
        </div>
      </div>

      <div className="animate-pulse">
        <div className="h-64 bg-gray-200 rounded"></div>
        <div className="mt-4 space-y-2">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    </div>
  );
  
  const hasAllResults = cameraAnalysis?.beamAngle != null && 
                       cameraAnalysis?.beamAngleUncertainty != null && 
                       Array.isArray(cameraAnalysis?.braggPeakPixel) &&
                       cameraAnalysis?.braggPeakPixel != null && 
                       cameraAnalysis?.braggPeakPixelUncertainty != null;
  console.log("HASSS ALL RESULTDS: ", hasAllResults)
  console.log("Beam Angle", cameraAnalysis?.beamAngle)
  console.log("Beam Angle unc", cameraAnalysis?.beamAngleUncertainty)
  console.log("peak pos", cameraAnalysis?.braggPeakPixel)
  console.log("peak pos unc", cameraAnalysis?.braggPeakPixelUncertainty)

  const canShowPlots = cameraAnalysis?.averageImage && 
                      cameraAnalysis?.colourChannel && 
                      hasAllResults;

  return (
    <div className="space-y-4">
      <div className="w-full">
        <table className="w-full text-sm">
          <tbody>
            <tr>
              <td className="px-4 py-2">
                <strong>Camera Username:</strong> {record?.username}
              </td>
              <td className="px-4 py-2">
                <strong>IP Address:</strong> {record?.ip_address}
              </td>
              <td className="px-4 py-2">
                <strong>Camera ID:</strong> {record?.id}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1">
          <ShowRealRunPhoto />
        </div>
        <div className="flex-1">
          {cameraAnalysis?.averageImage && cameraAnalysis?.colourChannel && (
            <div className="h-full flex items-center">
              <ShowAveragedPhoto
                imageUrl={imageUrl}
                colourChannel={cameraAnalysis.colourChannel}
              />
            </div>
          )}
        </div>
      </div>

      {hasAllResults && (
        <ShowResults
          beamAngle={cameraAnalysis.beamAngle}
          beamAngleUncertainty={cameraAnalysis.beamAngleUncertainty}
          braggPeakPixel={cameraAnalysis.braggPeakPixel}
          braggPeakPixelUncertainty={cameraAnalysis.braggPeakPixelUncertainty}
        />
      )}
      
      <div className="flex flex-col gap-4">
        <Button 
          onClick={() => setShowPlotsDialog(true)}
          className="w-fit"
          disabled={!canShowPlots}
        >
          View Analysis Plots
        </Button>
        {canShowPlots && (
          <Dialog open={showPlotsDialog} onOpenChange={setShowPlotsDialog}>
            <DialogContent className="max-w-[90vw] max-h-[90vh]">
              <DialogTitle>Analysis Plots</DialogTitle>
              <ShowPlots isOpen={showPlotsDialog} />
            </DialogContent>
          </Dialog>
        )}
      </div>
      
      <div>
        <DeleteButton record={record} onDelete={refetch} />
      </div>
    </div>
  )   
}