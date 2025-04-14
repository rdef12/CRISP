import { useParams } from "react-router-dom";
import { useShowController } from "react-admin";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export const ShowBraggPeakDepth = () => {
  const { beamRunId } = useParams();
  const { record, isPending, error } = useShowController({
    resource: `beam-run/bragg-peak`,
    id: beamRunId
  });

  // if (isPending) {
  //   return (
  //     <Card className="w-[400px]">
  //       <CardHeader>
  //         <Skeleton className="h-4 w-[100px]" />
  //       </CardHeader>
  //       <CardContent>
  //         <div className="space-y-2">
  //           {[...Array(4)].map((_, i) => (
  //             <Skeleton key={i} className="h-4 w-[300px]" />
  //           ))}
  //         </div>
  //       </CardContent>
  //     </Card>
  //   );
  // }
  if (isPending) return null;
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
        <span className="font-mono">{formatValue(record.bragg_peak_x, record.bragg_peak_x_unc) ?? "-"}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-muted-foreground">Y Position:</span>
        <span className="font-mono">{formatValue(record.bragg_peak_y, record.bragg_peak_y_unc) ?? "-"}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-muted-foreground">Z Position:</span>
        <span className="font-mono">{formatValue(record.bragg_peak_z, record.bragg_peak_z_unc) ?? "-"}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-muted-foreground">Depth:</span>
        <span className="font-mono">{formatValue(record.bragg_peak_depth, record.bragg_peak_depth_unc) ?? "-"}</span>
      </div>
    </div>
  );
};