import { useEffect, useState } from "react";
import { Datagrid, ListBase, TextField, useRecordContext, useShowController, useGetOne } from "react-admin";
import { useParams } from "react-router-dom";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { CreateRealSettings } from "./CreateRealSettings";
import { EditRealSettings } from "./EditRealSettings";
import { Button } from "@/components/ui/button";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card";
import { ShowRealRunPhoto } from "./ShowRealRunPhoto";
import { MoveToRealRunButton } from "./MoveToRealRunButton";

type DialogMode = 'create' | 'view' | null;

interface SettingsButtonProps {
  onSave: () => void;
}


const SettingsButton = ({ onSave }: SettingsButtonProps) => {
  const record = useRecordContext();
  const [dialogMode, setDialogMode] = useState<DialogMode>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [hasSettings, setHasSettings] = useState(false);
  const { beamRunId } = useParams();

  const { data: selectedCameraSettings } = useGetOne(
    record ? `settings/beam-run/real/${beamRunId}/camera` : '',
    // { meta: { enabled: !!record } }
    { id: record?.id }
  );

  useEffect(() => {
    if (selectedCameraSettings?.has_settings) {
      setHasSettings(true);
    }
    else setHasSettings(false)
  }, [selectedCameraSettings]);

  const handleCloseDialog = () => {
    console.log('SettingsButton: handleCloseDialog called');
    setDialogMode(null);
    setIsEditing(false);
  };

  const handleSettingsClick = () => {
    // Always show create if no settings exist
    setDialogMode(hasSettings ? 'view' : 'create');
  };

  const handleSave = () => {
    console.log('SettingsButton: handleSave called');
    onSave();
    handleCloseDialog();
  };

  const getDialogTitle = () => {
    if (dialogMode === 'create') return 'Create Settings';
    if (dialogMode === 'view') return isEditing ? 'Edit Settings' : 'View Settings';
    return '';
  };

  return (
    <>
      <Dialog open={dialogMode !== null} onOpenChange={handleCloseDialog} >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {getDialogTitle()}
            </DialogTitle>
          </DialogHeader>
          <ScrollArea className="h-[60vh]">
            {record && dialogMode === 'create' && (
              <CreateRealSettings record={record} onSave={handleSave} />
            )}
            {record && dialogMode === 'view' && hasSettings && (
              <EditRealSettings 
                record={record} 
                onSave={handleSave} 
                onEditStateChange={() => setIsEditing(true)}
              />
            )}
          </ScrollArea>
        </DialogContent>
      </Dialog>

      <div className="w-[140px]">
        <HoverCard>
          <HoverCardTrigger asChild>
            <Button 
              variant={hasSettings ? "outline" : "red"}
              onClick={(e) => {
                e.stopPropagation();
                handleSettingsClick();
              }}
              className="w-full"
            >
              {hasSettings ? 'View Settings' : 'Create Settings'}
            </Button>
          </HoverCardTrigger>
          <HoverCardContent variant={hasSettings ? "default" : "red"} className="w-80">
            <div className="space-y-1">
              <h4 className="text-sm font-semibold">Camera Settings</h4>
              <p className="text-sm">
                {hasSettings 
                  ? <>View or modify the current camera settings</>
                  : <>No tested camera settings found for these beam parameters.<br/> Perform a test run or manually input here. </>}
              </p>
            </div>
          </HoverCardContent>
        </HoverCard>
      </div>
    </>
  );
};

export const ListCamerasInExperimentReal = ({ dataTaken } : { dataTaken: boolean }) => {
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

  if (!dataTaken) return (
    <ListBase resource={resource}>
      <Datagrid 
        data={record.cameras} 
        bulkActionButtons={false}
        rowClick={false}
        hover={false}
      >
        <TextField source="username" />
        <TextField source="ip_address" />
        <SettingsButton onSave={handleSave} />
      </Datagrid>
      <MoveToRealRunButton />
    </ListBase>
  );

  return (
    <ListBase resource={resource}>
      <Datagrid 
        data={record.cameras} 
        bulkActionButtons={false}
        expand={<ShowRealRunPhoto />}
      >
        <TextField source="username" />
        <TextField source="ip_address" />
      </Datagrid>
    </ListBase>
  );
};

