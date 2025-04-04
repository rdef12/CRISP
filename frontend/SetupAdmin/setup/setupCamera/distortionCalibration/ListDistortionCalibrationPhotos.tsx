import { useGetList, useDelete } from "react-admin";
import { useParams } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";
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
import { useEffect } from "react";

export const DeleteButton = ({ record, onDelete }: { record: { id: string }, onDelete: () => void }) => {
  const [deleteOne] = useDelete();

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await deleteOne(
      `photo`,
      { id: record.id },
      {
        onSuccess: () => {
          onDelete();
        },
      }
    );
  };

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button 
          variant="destructive" 
          size="icon" 
          className="absolute top-0 right-0 z-10"
          onClick={(e) => e.stopPropagation()}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This will delete the calibration photo. This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={(e) => e.stopPropagation()}>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

interface ListDistortionCalibrationPhotosProps {
  shouldRefresh: boolean;
  onRefreshComplete: () => void;
}

export const ListDistortionCalibrationPhotos = ({ shouldRefresh, onRefreshComplete }: ListDistortionCalibrationPhotosProps) => {
  const { setupCameraId } = useParams();
  const { data, isPending, refetch } = useGetList( `photo/distortion-calibration/${setupCameraId}` );

  useEffect(() => {
    if (shouldRefresh) {
      refetch();
      onRefreshComplete();
    }
  }, [shouldRefresh, refetch, onRefreshComplete]);

  if (isPending) return null;
  
  return (
    <ScrollArea
    // className="h-72 w-48 rounded-md border" 
    className="h-full"
    >
      <div className="space-y-1 p-4">
        {data?.map((item) => (
          <Card key={item.id}>
            <CardContent className="p-1 relative">
              <img 
                src={`data:image/jpeg;base64,${item.photo}`}
                alt="Calibration photo" 
                className="w-full max-h-[150px] object-contain"
              />
              <DeleteButton record={item} onDelete={refetch} />
            </CardContent>
          </Card>
        ))}
      </div>
    </ScrollArea>
  );
}