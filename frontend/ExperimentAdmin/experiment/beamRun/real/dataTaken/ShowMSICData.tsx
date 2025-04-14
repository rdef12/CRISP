import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useShowController } from "react-admin";
import { useParams } from "react-router-dom";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { EditMSICData } from "./EditMSICData";

export const ShowMSICData = () => {
  const { beamRunId } = useParams();
  const { record, isPending, error } = useShowController({
    resource: `beam-run/MSIC`,
    id: beamRunId,
  });
  const [isEditOpen, setIsEditOpen] = useState(false);

  if (isPending) {
    return (
      <Card className="w-full">
        <CardHeader>
          <Skeleton className="h-4 w-[100px]" />
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[...Array(2)].map((_, i) => (
              <Skeleton key={i} className="h-4 w-[300px]" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return <div className="text-red-500">Error loading data</div>;
  }

  const formatValue = (value: number | null | undefined, uncertainty: number | null | undefined, unit: string) => {
    if (value === null || value === undefined) {
      return "-";
    }
    if (uncertainty === null || uncertainty === undefined) {
      return `${value} ${unit}`;
    }
    return `${value} ± ${uncertainty} ${unit}`;
  };

  const allValuesNull = !record.MSIC_energy && !record.MSIC_energy_uncertainty && 
                       !record.MSIC_current && !record.MSIC_current_uncertainty;

  return (
    <>
      <Card className="w-[400px] h-full">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>MSIC Measurements</CardTitle>
          <Button
            variant="outline"
            onClick={() => setIsEditOpen(true)}
          >
            {allValuesNull ? "Add" : "Edit"}
          </Button>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Energy:</span>
              <span className="font-mono">{formatValue(record.MSIC_energy, record.MSIC_energy_uncertainty, "MeV")}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Beam Current:</span>
              <span className="font-mono">{formatValue(record.MSIC_current, record.MSIC_current_uncertainty, "nA")}</span>
            </div>
          </div>
        </CardContent>
      </Card>
      {isEditOpen && <EditMSICData onClose={() => setIsEditOpen(false)} />}
    </>
  );
};