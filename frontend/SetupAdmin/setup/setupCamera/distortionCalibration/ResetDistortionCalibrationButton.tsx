import { Button } from "@/components/ui/button";
import { useDelete } from "react-admin";
import { useParams } from "react-router-dom";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

export const ResetDistortionCalibrationButton = () => {
  const { setupCameraId } = useParams();
  const [deleteOne, { isPending, error }] = useDelete(
    'setup-camera/distortion-calibration/reset',
    { id: setupCameraId}
  );
  
  const handleConfirm = () => {
    deleteOne();
  };
  
  return (
    <div>
      <AlertDialog>
        <AlertDialogTrigger asChild>
          <Button disabled={isPending}>
            Reset distortion calibration
          </Button>
        </AlertDialogTrigger>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirm Reset</AlertDialogTitle>
            <AlertDialogDescription>
              WARNING: All sections of this camera's calibration in this setup will be reset. This cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirm} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Reset
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
      
      {/* {Boolean(error) && (
        <div className="mt-2 p-3 text-sm text-red-500 bg-red-50 rounded-md border border-red-200">
          Error occurred while resetting calibration
        </div>
      )} */}
    </div>
  );
}