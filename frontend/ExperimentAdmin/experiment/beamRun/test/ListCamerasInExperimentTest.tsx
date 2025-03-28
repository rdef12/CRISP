import { Datagrid, TextField, useGetList, useShowController, useRecordContext, ListBase, useDataProvider } from "react-admin";
import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { CreateTestSettings } from "./CreateTestSettings";
import { EditTestSettings } from "./EditTestSettings";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { ListTestSettings } from "./ListTestSettings";

type DialogMode = 'create' | 'edit' | null;

interface SettingsButtonProps {
  onSave: () => void;
}

const SettingsButton = ({ onSave }: SettingsButtonProps) => {
  const record = useRecordContext();
  const [dialogMode, setDialogMode] = useState<DialogMode>(null);
  const [hasSettings, setHasSettings] = useState(false);
  const { beamRunId } = useParams();

  const { data: selectedCameraSettings } = useGetList(
    record ? `settings/beam-run/test/${beamRunId}/camera/${record.id}` : '',
    // { meta: { enabled: !!record } }
  );

  useEffect(() => {
    if (selectedCameraSettings) {
      setHasSettings(selectedCameraSettings.length > 0);
    }
  }, [selectedCameraSettings]);

  const handleCloseDialog = () => {
    console.log('SettingsButton: handleCloseDialog called');
    setDialogMode(null);
  };

  const handleSettingsClick = () => {
    setDialogMode(hasSettings ? 'edit' : 'create');
  };

  const handleSave = () => {
    console.log('SettingsButton: handleSave called');
    onSave();
    handleCloseDialog();

  };

  return (
    <>
      <Dialog open={dialogMode !== null} onOpenChange={handleCloseDialog} >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {dialogMode === 'create' ? 'Create Test Settings' : 'Edit Test Settings'}
            </DialogTitle>
          </DialogHeader>
          {/* <ScrollArea className="h-[60vh]"> */}
            {record && dialogMode === 'create' && (
              <CreateTestSettings record={record} onSave={handleSave} />
            )}
            {record && dialogMode === 'edit' && (
              <EditTestSettings record={record} onSave={handleSave} />
            )}
          {/* </ScrollArea> */}
        </DialogContent>
      </Dialog>

      <div className="w-[140px]">
        <Button 
          variant="outline" 
          onClick={(e) => {
            e.stopPropagation();
            handleSettingsClick();
          }}
          className="w-full"
        >
          {hasSettings ? 'Edit Settings' : 'Create Settings'}
        </Button>
      </div>
    </>
  );
};

export const ListCamerasInExperimentTest = () => {
  // const dataProvider = useDataProvider();
  const { experimentId } = useParams();
  const [refreshTrigger, setRefreshTrigger] = useState(false);
  const { isPending, resource, record } = useShowController({ 
    resource: `experiment`, 
    id: experimentId, 
    queryOptions: { meta: { setup: "setup", cameras: "cameras" }}
  });

  if (isPending) return null;

  const handleSave = () => {
    setRefreshTrigger(!refreshTrigger);
  };

  return (
    <ListBase resource={resource}>
      <Datagrid 
        data={record.cameras} 
        bulkActionButtons={false}
        expand={<ListTestSettings refreshTrigger={refreshTrigger} />}
      >
        <TextField source="username" />
        <TextField source="ip_address" />
        <SettingsButton onSave={handleSave} />
      </Datagrid>
    </ListBase>
  )
}

export const ListCamerasInExperimentReal = () => {
  return (
    <div>
      
    </div>
  )
}
