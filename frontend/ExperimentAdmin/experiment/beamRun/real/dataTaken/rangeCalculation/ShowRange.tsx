import { Card } from "@/components/ui/card";
import { useGetOne, useRecordContext } from "react-admin";
import { useParams } from "react-router-dom";
import { useEffect } from "react";

interface ShowRangeProps {
  isSaving: boolean;
  onSaveComplete: () => void;
}

export const ShowRange = ({ isSaving, onSaveComplete }: ShowRangeProps) => {
  const { beamRunId } = useParams();
  const record = useRecordContext();
  const { data, isPending, refetch } = useGetOne(
   `beam-run/range/${beamRunId}/camera`,
    {id: record?.id}
  )

  useEffect(() => {
    if (isSaving) {
      refetch().then(() => {
        onSaveComplete();
      });
    }
  }, [isSaving, refetch, onSaveComplete]);

  if (isPending) return null;
  if (isSaving) return (
    <Card>
      <div className="animate-pulse">
        <div className="h-64 bg-gray-200 rounded"></div>
      </div>
    </Card>
  )
  return (
    <div className="space-y-4">
      <Card className="p-4">
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold mb-2">Range Analysis</h3>
            <div>
              <p className="text-sm font-medium">Range:</p>
              <p className="text-sm">
                {data?.range ? `${data.range} ± ${data.range_uncertainty} mm` : "-"}
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}