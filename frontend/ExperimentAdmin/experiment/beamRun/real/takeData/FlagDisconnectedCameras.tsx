import { useParams } from "react-router-dom";
import { RaRecord, useShowController, useListController } from "react-admin";


interface ExperimentCamera extends RaRecord {
  id: number;
  username: string;
  ip_address: string;
}

export const FlagDisconnectedCameras = () => {
  const { experimentId } = useParams();
  
  // Get all camera statuses
  const { isPending: isPendingStatuses, data: cameraStatuses } = useListController({
    resource: 'camera/statuses',
    queryOptions: { refetchInterval: 500 }
  });

  // Get experiment cameras
  const { isPending: isPendingExperiment, record } = useShowController({ 
    resource: `experiment`, 
    id: experimentId, 
    queryOptions: { meta: { setup: "setup", cameras: "cameras" }}
  });

  if (isPendingStatuses || isPendingExperiment) {
    return (
      <div className="p-4">
        <div className="animate-pulse flex space-x-4">
          <div className="flex-1 space-y-4 py-1">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!cameraStatuses || !record?.cameras || record.cameras.length === 0) {
    return (
      <div className="p-4 text-gray-600 text-center">
        No cameras found in the system
      </div>
    );
  }

  // Filter camera statuses to only include cameras in this experiment
  const experimentCameraIds = (record.cameras as ExperimentCamera[]).map(camera => camera.id);
  const relevantCameras = cameraStatuses.filter(camera => 
    experimentCameraIds.includes(Number(camera.id))
  );

  const connectedCameras = relevantCameras.filter(camera => camera.connectionStatus);
  const disconnectedCameras = relevantCameras.filter(camera => !camera.connectionStatus);

  return (
    <div className="p-4 space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Connected Cameras */}
        <div className="bg-green-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-green-700 mb-2">
            Connected Cameras ({connectedCameras.length})
          </h3>
          <div className="space-y-2">
            {connectedCameras.map((camera) => (
              <div
                key={camera.username}
                className="bg-white p-3 rounded shadow-sm border border-green-200"
              >
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <div>
                    <p className="font-medium">{camera.username}</p>
                    <p className="text-sm text-gray-600">
                      {camera.cameraModel} - {camera.IPAddress}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Disconnected Cameras */}
        <div className="bg-red-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-red-700 mb-2">
            Disconnected Cameras ({disconnectedCameras.length})
          </h3>
          <div className="space-y-2">
            {disconnectedCameras.map((camera) => (
              <div
                key={camera.username}
                className="bg-white p-3 rounded shadow-sm border border-red-200"
              >
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <div>
                    <p className="font-medium">{camera.username}</p>
                    <p className="text-sm text-gray-600">
                      {camera.cameraModel} - {camera.IPAddress}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};