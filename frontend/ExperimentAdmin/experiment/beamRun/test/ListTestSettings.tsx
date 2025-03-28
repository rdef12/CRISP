import { useParams } from "react-router-dom";
import { Datagrid, ListBase, NumberField, useRecordContext, useDataProvider } from "react-admin";
import { useEffect, useState } from "react";

interface ListTestSettingsProps {
  refreshTrigger?: boolean;
}

export const ListTestSettings = ({ refreshTrigger }: ListTestSettingsProps) => {
  const { beamRunId } = useParams();
  const record = useRecordContext();
  const dataProvider = useDataProvider();
  const [data, setData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  console.log('[Settings] Render with refreshTrigger:', refreshTrigger);
  
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

  console.log('[Settings] Rendering List with data:', data);
  return (
    <ListBase
      resource={`settings/beam-run/test/${beamRunId}/camera/${record.id}`}
    >
      <Datagrid bulkActionButtons={false}>
        <NumberField source="gain" />
        <NumberField source="frame_rate" />
        <NumberField source="lens_position" />
      </Datagrid>
    </ListBase>
  );
}