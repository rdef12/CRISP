import { useParams } from "react-router-dom";
import { Datagrid, ListBase, NumberField, useRecordContext, useDataProvider, BooleanField } from "react-admin";
import { useEffect, useState } from "react";
import { Card, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

interface TestSetting {
  id: number;
  gain: number;
  frame_rate: number;
  lens_position: number;
}

interface ListTestSettingsProps {
  refreshTrigger?: boolean;
  dataTaken?: boolean
}

export const ListTestSettings = ({ refreshTrigger, dataTaken }: ListTestSettingsProps) => {
  const { beamRunId } = useParams();
  const record = useRecordContext();
  const dataProvider = useDataProvider();
  const [data, setData] = useState<TestSetting[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  console.log('[Settings] Render with refreshTrigger:', refreshTrigger);
  console.log('IM IN THE THING Data taken. ', dataTaken)
  const fetchData = async () => {
    if (!record) return;
    
    try {
      setIsLoading(true);
      const response = await dataProvider.getList(
        `settings/beam-run/test/${beamRunId}/camera/${record.id}`,
        {
          pagination: { page: 1, perPage: 25 },
          sort: { field: 'id', order: 'DESC' },
          filter: {}
        }
      );
      
      console.log('[Settings] Data fetched successfully:', response.data);
      setData(response.data);
    } catch (error) {
      console.error('[Settings] Error fetching data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [refreshTrigger, record, beamRunId]);

  if (!record) return null;

  if (isLoading) {
    console.log('[Settings] Loading state');
    return (
      <div className="p-4 text-center">
        Loading settings...
      </div>
    );
  }

  const sumOfReciprocals = data.reduce((sum, setting) => sum + (1 / setting.frame_rate), 0);
  const numberOfPhotos = data.length

  console.log('[Settings] Rendering List with data:', data);
  
  if (!dataTaken) return (
    <div>
        <Card>
          <CardHeader>
            <CardTitle>Minimum time for data collection: {sumOfReciprocals.toFixed(2)} s</CardTitle>
          </CardHeader>
          <CardFooter> Number of photos: {numberOfPhotos}</CardFooter>
        </Card>
      <ListBase
        resource={`settings/beam-run/test/${beamRunId}/camera/${record.id}`}
      >
        <Datagrid bulkActionButtons={false}>
          <NumberField source="gain" />
          <NumberField source="frame_rate" />
          <NumberField source="lens_position" />
        </Datagrid>
      </ListBase>
    </div>
  );

  if (dataTaken) return (
    <div>
        <Card>
          <CardHeader>
            <CardTitle>Minimum time for data collection: {sumOfReciprocals.toFixed(2)} s</CardTitle>
          </CardHeader>
          <CardFooter> Number of photos: {numberOfPhotos}</CardFooter>
        </Card>
      <ListBase
        resource={`settings/beam-run/test/${beamRunId}/camera/${record.id}`}
      >
        <Datagrid bulkActionButtons={false}>
          <NumberField source="gain" />
          <NumberField source="frame_rate" />
          <NumberField source="lens_position" />
          <BooleanField source="is_optimal" />
        </Datagrid>
      </ListBase>
    </div>
  )
}