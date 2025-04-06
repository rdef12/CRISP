import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useDataProvider } from "react-admin";
import { useParams } from "react-router-dom";
import { ImageOverlayCarousel } from "./ImageOverlayCarousel";

interface TestSetting {
  id: number;
  camera_settings_id: number;
  gain: number;
  frame_rate: number;
  lens_position: number;
  is_optimal?: boolean;
}

interface ShowTestRunPhotoProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  selectedSetting: TestSetting | null;
  onSubmit: () => void;
  onRefresh: () => void;
}



export const ShowTestRunPhoto = ({ isOpen, onOpenChange, selectedSetting, onSubmit, onRefresh }: ShowTestRunPhotoProps) => {
  const { beamRunId } = useParams();
  const dataProvider = useDataProvider();
  
  // const { data: imageData, isLoading } = useGetOne(
  //   `photo/beam-run/test/${beamRunId}/camera-settings`,
  //   { id: selectedSetting?.camera_settings_id },
  //   { enabled: !!selectedSetting && isOpen }
  // );



  const handleSubmit = async () => {
    if (!selectedSetting) return;
    
    try {
      await dataProvider.update(
        `settings/beam-run/test/${beamRunId}/camera-settings`,
        {
          id: selectedSetting.camera_settings_id,
          data: {},
          previousData: selectedSetting
        }
      );
      onRefresh();
      onSubmit();
    } catch (error) {
      console.error('Error updating setting:', error);
      // You might want to show an error message to the user here
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] flex flex-col [&>button]:hidden">
        <DialogHeader className="flex-none border-b pb-4">
          <div className="flex items-center w-full">
            <DialogTitle className="flex-none">Test Setting Details</DialogTitle>
            <div className="flex-1 flex ml-8 gap-2">
              <Button onClick={handleSubmit} variant="green" className="flex-1">
                Select as optimal settings
              </Button>
              <Button onClick={() => onOpenChange(false)} variant="red" className="flex-1">
                Cancel
              </Button>
            </div>
          </div>
          {selectedSetting && (
            <table className="w-full text-sm mt-4">
              <tbody>
                <tr>
                  <td className="px-4 py-2">
                    <strong>Gain:</strong> {selectedSetting.gain}
                  </td>
                  <td className="px-4 py-2">
                    <strong>Frame Rate:</strong> {selectedSetting.frame_rate}
                  </td>
                  <td className="px-4 py-2">
                    <strong>Lens Position:</strong> {selectedSetting.lens_position}
                  </td>
                  <td className="px-4 py-2">
                    <strong>Is Optimal:</strong> {selectedSetting.is_optimal ? "Yes" : "No"}
                  </td>
                  <td className="px-4 py-2">
                    <strong>ID:</strong> {selectedSetting.id}
                  </td>
                  <td className="px-4 py-2">
                    <strong>Camera Settings ID:</strong> {selectedSetting.camera_settings_id}
                  </td>
                </tr>
              </tbody>
            </table>
          )}
        </DialogHeader>

        <ImageOverlayCarousel selectedSetting={selectedSetting}/>
      </DialogContent>
    </Dialog>
  );
}; 

// {selectedSetting && (
//   <div className="flex-1 overflow-y-auto space-y-4 mt-4">
//     {/* Image Display */}
//     <div className="w-full">
//       {isLoading ? (
//         <div className="text-center">Loading image...</div>
//       ) : imageUrl ? (
//         <div className="relative w-full overflow-hidden rounded-lg">
//           <img 
//             src={imageUrl} 
//             alt="Test Run Photo"
//             className="w-full object-contain"
//             onError={(e) => console.error('Image loading error:', e)}
//           />
//         </div>
//       ) : (
//         <div className="text-center text-gray-500">No image available</div>
//       )}
//     </div>
//   </div>
// )}