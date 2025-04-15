import { useParams } from "react-router-dom";
import { Datagrid, ListBase, NumberField, useRecordContext, useDataProvider, BooleanField, RaRecord, Identifier } from "react-admin";
import { useEffect, useState } from "react";
import { Card, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { ShowTestRunPhoto } from "./ShowTestRunPhoto";
import { useTestData } from "./TestDataContext";

interface TestSetting {
  id: number;
  camera_settings_id: number;
  gain: number;
  frame_rate: number;
  lens_position: number;
  is_optimal?: boolean;
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
  const [selectedSetting, setSelectedSetting] = useState<TestSetting | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const { setDuration } = useTestData();
  
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

  const handleRowClick = (id: Identifier, resource: string, record: RaRecord): false => {
    setSelectedSetting(record as TestSetting);
    setIsDialogOpen(true);
    return false;
  };

  const sumOfReciprocals = data.reduce((sum, setting) => sum + (1 / setting.frame_rate), 0);
  const numberOfPhotos = data.length;
  const duration = sumOfReciprocals + numberOfPhotos * 0.77 + numberOfPhotos; //CONSTRAINTS: frame rate, write time, copy time

  useEffect(() => {
    setDuration(duration);
  }, [duration, setDuration]);

  if (!record) return null;

  if (isLoading) {
    console.log('[Settings] Loading state');
    return (
      <div className="p-4 text-center">
        Loading settings...
      </div>
    );
  }

  console.log('[Settings] Rendering List with data:', data);
  
  if (!dataTaken) return (
    <div>
        <Card>
          <CardHeader>
            <CardTitle>Minimum estimated time for data collection: {duration.toFixed(2)} s</CardTitle>
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

  const handleSubmit = () => {
    // This is where you'll add your form submission logic
    setIsDialogOpen(false);
  };

  return (
    <div>
      <Card>
        <CardHeader>
          <CardTitle>Minimum estimated time for data collection: {duration.toFixed(2)} s</CardTitle>
        </CardHeader>
        <CardFooter> Number of photos: {numberOfPhotos}</CardFooter>
      </Card>
      <ListBase
        resource={`settings/beam-run/test/${beamRunId}/camera/${record.id}`}
      >
        <Datagrid 
          bulkActionButtons={false}
          rowClick={(id, resource, record) => handleRowClick(id, resource, record)}
        >
          <NumberField source="gain" />
          <NumberField source="frame_rate" />
          <NumberField source="lens_position" />
          <BooleanField source="is_optimal" />
        </Datagrid>
      </ListBase>

      <ShowTestRunPhoto
        isOpen={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        selectedSetting={selectedSetting}
        onSubmit={handleSubmit}
        onRefresh={fetchData}
      />
    </div>
  );
}