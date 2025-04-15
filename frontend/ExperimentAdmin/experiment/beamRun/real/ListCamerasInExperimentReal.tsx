import { useEffect, useState } from "react";
import { Datagrid, ListBase, TextField, useRecordContext, useShowController, useGetOne } from "react-admin";
import { useParams } from "react-router-dom";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { CreateRealSettings } from "./dataNotTaken/CreateRealSettings";
import { EditRealSettings } from "./dataNotTaken/EditRealSettings";
import { Button } from "@/components/ui/button";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card";
import { MoveToRealRunButton } from "./dataNotTaken/MoveToRealRunButton";
import { EditNumberOfImagesAndRaw } from "./dataNotTaken/EditNumberOfImagesAndRaw";
import { ShowCameraWithData } from "./dataTaken/ShowCameraWithData";
import { useRealData } from "./RealDataContext";

type DialogMode = 'create' | 'view' | null;

interface SettingsButtonProps {
  onSave: () => void;
  refreshTrigger?: boolean;
}

const SettingsButton = ({ onSave, refreshTrigger }: SettingsButtonProps) => {
  const record = useRecordContext();
  const [dialogMode, setDialogMode] = useState<DialogMode>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [hasSettings, setHasSettings] = useState(false);
  const { beamRunId } = useParams();

  const { data: selectedCameraSettings } = useGetOne(
    record ? `settings/beam-run/real/${beamRunId}/camera` : '',
    { 
      id: record?.id,
      meta: { refresh: refreshTrigger }
    }
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

const NumberOfImagesButton = ({ onSave, refreshTrigger }: SettingsButtonProps) => {
  const record = useRecordContext();
  const [dialogMode, setDialogMode] = useState<DialogMode>(null);
  const [hasSettings, setHasSettings] = useState(false);
  const { beamRunId } = useParams();

  const { data: selectedCameraSettings } = useGetOne(
    record ? `settings/beam-run/real/${beamRunId}/camera` : '',
    { 
      id: record?.id,
      meta: { refresh: refreshTrigger }
    }
  );

  const { data: selectedNumberOfImages, refetch: refetchNumberOfImages } = useGetOne(
    record ? `camera-settings/beam-run/real/${beamRunId}/camera` : '',
    {
      id: record?.id,
      meta: { refresh: refreshTrigger }
    }
  );

  useEffect(() => {
    if (selectedCameraSettings?.has_settings) {
      setHasSettings(true);
    }
    else setHasSettings(false)
  }, [selectedCameraSettings]);

  const handleCloseDialog = () => {
    setDialogMode(null);
  };

  const handleSettingsClick = () => {
    setDialogMode('view');
  };

  const handleSave = () => {
    onSave();
    refetchNumberOfImages();
    handleCloseDialog();
  };

  return (
    <>
      <Dialog open={dialogMode !== null} onOpenChange={handleCloseDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              Edit Image Collection
            </DialogTitle>
          </DialogHeader>
          <ScrollArea className="h-[60vh]">
            {record && dialogMode === 'view' && (
              <EditNumberOfImagesAndRaw 
                record={record} 
                onSave={handleSave} 
                onEditStateChange={() => {}}
                refreshTrigger={refreshTrigger}
              />
            )}
          </ScrollArea>
        </DialogContent>
      </Dialog>

      <div className="w-[140px]">
        <HoverCard>
          <HoverCardTrigger asChild>
            <Button 
              variant={selectedNumberOfImages?.has_settings ? "outline" : "red"}
              onClick={(e) => {
                e.stopPropagation();
                if (hasSettings) {
                  handleSettingsClick();
                }
              }}
              className="w-full"
              disabled={!hasSettings}
            >
              Edit Image Collection
            </Button>
          </HoverCardTrigger>
          <HoverCardContent variant={selectedNumberOfImages?.has_settings ? "default" : "red"} className="w-80">
            <div className="space-y-1">
              <h4 className="text-sm font-semibold">Image Settings</h4>
              <p className="text-sm">
                {!hasSettings 
                  ? <>No camera settings found. Please create settings first.</>
                  : selectedNumberOfImages?.has_settings 
                    ? <>Edit the number of images and raw image settings for this camera</>
                    : <>No image settings found. Click to set up image settings.</>}
              </p>
            </div>
          </HoverCardContent>
        </HoverCard>
      </div>
    </>
  );
};

const TimeToTakeData = ({ refreshTrigger }: { refreshTrigger?: boolean }) => {
  const record = useRecordContext();
  const { beamRunId } = useParams();
  const { setDuration } = useRealData();

  const { data, isLoading } = useGetOne(
    `camera-settings/time-to-take-data/${beamRunId}/camera`,
    { 
      id: record?.id || '',
      meta: { refresh: refreshTrigger }
    }
  );

  useEffect(() => {
    if (data?.duration != null) {
      setDuration(data.duration);
    }
  }, [data, setDuration]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!data || !record) {
    return <div>No data available</div>;
  }
  const duration = data?.duration;
  return (
    <div className="w-[140px]">
      <HoverCard>
        <HoverCardTrigger asChild>
          { duration != null && (
            <Button variant="outline" className="w-full">
              Estimated duration: {(duration)} s
            </Button>
          )}
        </HoverCardTrigger>
        <HoverCardContent className="w-80">
          <div className="space-y-1">
            <h4 className="text-sm font-semibold">Estimated Time</h4>
            <p className="text-sm">
              This is the estimated minimum time required to take all images with the current settings.
            </p>
          </div>
        </HoverCardContent>
      </HoverCard>
    </div>
  );
};

interface ListCamerasInExperimentRealProps {
  dataTaken: boolean;
  onCameraAnalysisCreated: () => void;
  onAnalysisDeleted?: () => void;
}

export const ListCamerasInExperimentReal = ({ 
  dataTaken, 
  onCameraAnalysisCreated,
  onAnalysisDeleted 
}: ListCamerasInExperimentRealProps) => {
  const { experimentId } = useParams();
  const [refreshTrigger, setRefreshTrigger] = useState(false);
  const { isPending, resource, record } = useShowController({ 
    resource: `experiment`, 
    id: experimentId, 
    queryOptions: { meta: { setup: "setup", cameras: "cameras" }}
  });

  const handleSave = () => {
    setRefreshTrigger(!refreshTrigger);
  };

  if (isPending) return null;

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
        <SettingsButton onSave={handleSave} refreshTrigger={refreshTrigger} />
        <NumberOfImagesButton 
          onSave={handleSave} 
          refreshTrigger={refreshTrigger}
        />
        <TimeToTakeData refreshTrigger={refreshTrigger} />
      </Datagrid>
      <MoveToRealRunButton refreshTrigger={refreshTrigger} />
    </ListBase>
  );

  return (
    <ListBase resource={resource}>
      <Datagrid 
        data={record.cameras} 
        bulkActionButtons={false}
        expand={<ShowCameraWithData 
          onCameraAnalysisCreated={onCameraAnalysisCreated} 
          onAnalysisDeleted={onAnalysisDeleted}
        />}
      >
        <TextField source="username" />
        <TextField source="ip_address" />
      </Datagrid>
    </ListBase>
  );
};

