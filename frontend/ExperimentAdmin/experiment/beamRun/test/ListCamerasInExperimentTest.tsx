import { Datagrid, List, TextField, useGetList, useShowController, useRecordContext } from "react-admin";
import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { CreateTestSettings } from "./CreateTestSettings";
import { EditTestSettings } from "./EditTestSettings";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ListTestSettings } from "./ListTestSettings";

type DialogMode = 'create' | 'edit' | null;

const SettingsButton = () => {
  const record = useRecordContext();
  const [dialogMode, setDialogMode] = useState<DialogMode>(null);
  const [hasSettings, setHasSettings] = useState(false);
  const { beamRunId } = useParams();

  const { data: selectedCameraSettings } = useGetList(
    record ? `settings/beam-run/test/${beamRunId}/camera/${record.id}` : '',
    { meta: { enabled: !!record } }
  );

  useEffect(() => {
    if (selectedCameraSettings) {
      setHasSettings(selectedCameraSettings.length > 0);
    }
  }, [selectedCameraSettings]);

  const handleCloseDialog = () => {
    setDialogMode(null);
  };

  const handleSettingsClick = () => {
    setDialogMode(hasSettings ? 'edit' : 'create');
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
          <ScrollArea className="h-[60vh]">
            {record && dialogMode === 'create' && (
              <CreateTestSettings record={record} />
            )}
            {record && dialogMode === 'edit' && (
              <EditTestSettings record={record} />
            )}
          </ScrollArea>
        </DialogContent>
      </Dialog>

      <Button 
        variant="outline" 
        onClick={(e) => {
          e.stopPropagation();
          handleSettingsClick();
        }}
      >
        {hasSettings ? 'Edit Settings' : 'Create Settings'}
      </Button>
    </>
  );
};

export const ListCamerasInExperimentTest = () => {
  const { isPending, resource, record } = useShowController({ 
    resource: `experiment`, 
    id: useParams().experimentId, 
    queryOptions: { meta: { setup: "setup", cameras: "cameras" }}
  });

  if (isPending) return null;

  return (
    <List resource={resource}>
      <Datagrid 
        data={record.cameras} 
        bulkActionButtons={false}
        expand={<ListTestSettings />}
      >
        <TextField source="username" />
        <TextField source="ip_address" />
        <SettingsButton />
      </Datagrid>
    </List>
  )
}

export const ListCamerasInExperimentReal = () => {
  return (
    <div>
      
    </div>
  )
}
