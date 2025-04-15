import { useParams } from "react-router-dom";
import { useGetOne } from "react-admin";
import { useEffect } from "react";

interface ShowBraggPeakDepthProps {
  isCreating?: boolean;
}

interface BraggPeakRecord {
  id: string;
  bragg_peak_x: number | null;
  bragg_peak_x_unc: number | null;
  bragg_peak_y: number | null;
  bragg_peak_y_unc: number | null;
  bragg_peak_z: number | null;
  bragg_peak_z_unc: number | null;
  bragg_peak_depth: number | null;
  bragg_peak_depth_unc: number | null;
}

export const ShowBraggPeakDepth = ({ isCreating }: ShowBraggPeakDepthProps) => {
  const { beamRunId } = useParams();
  const { data: record, isLoading, error, refetch } = useGetOne<BraggPeakRecord>(
    `beam-run/bragg-peak`,
    { id: beamRunId }
  );

  useEffect(() => {
    if (isCreating === false) {
      refetch();
    }
  }, [isCreating, refetch]);

  console.log("ShowBraggPeakDepth - isCreating:", isCreating, "isLoading:", isLoading);

  if (isLoading || isCreating) {
    console.log("Showing loading spinner");
    return (
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
    );
  }
  if (error) {
    return <div className="text-red-500">Error loading data</div>;
  }

  const formatValue = (value: number | null | undefined, uncertainty: number | null | undefined) => {
    if (value === null || value === undefined) {
      return null;
    }
    if (uncertainty === null || uncertainty === undefined) {
      return `${value.toFixed(2)} mm`;
    }
    return `${value.toFixed(2)} ± ${uncertainty.toFixed(2)} mm`;
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between">
        <span className="text-muted-foreground">X Position:</span>
        <span className="font-mono">{formatValue(record?.bragg_peak_x, record?.bragg_peak_x_unc) ?? "-"}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-muted-foreground">Y Position:</span>
        <span className="font-mono">{formatValue(record?.bragg_peak_y, record?.bragg_peak_y_unc) ?? "-"}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-muted-foreground">Z Position:</span>
        <span className="font-mono">{formatValue(record?.bragg_peak_z, record?.bragg_peak_z_unc) ?? "-"}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-muted-foreground">Depth:</span>
        <span className="font-mono">{formatValue(record?.bragg_peak_depth, record?.bragg_peak_depth_unc) ?? "-"}</span>
      </div>
    </div>
  );
};