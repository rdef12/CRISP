import { Button } from "@/components/ui/button";
import { useDelete, useGetList, useRecordContext } from "react-admin";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";

interface Photo {
  id: number;
  photo: string;
}

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
          className="w-full"
          onClick={(e) => e.stopPropagation()}
        >
          Delete Photo
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>YOU ARE DELETING BEAM LINE DATA!!</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to proceed? This action cannot be undone.
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


export const ShowRealRunPhoto = () => {
  const { beamRunId } = useParams();
  const [imageUrls, setImageUrls] = useState<string[]>([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const record = useRecordContext();
  
  const { data, isLoading, refetch } = useGetList<Photo>(
    `photo/beam-run/real/${beamRunId}/camera/${record?.id}`,
  );
  const photos = data as Photo[] | undefined;

  useEffect(() => {
    console.log('Photos data:', photos);
    if (photos) {
      const urls = photos.map((photo: Photo) => `data:image/jpeg;base64,${photo.photo}`);
      console.log('Generated URLs:', urls);
      console.log('Number of images:', urls.length);
      setImageUrls(urls);
    }
  }, [photos]);

  const handlePhotoDelete = () => {
    refetch();
    if (currentImageIndex >= imageUrls.length - 1) {
      setCurrentImageIndex(Math.max(0, imageUrls.length - 2));
    }
    setIsDialogOpen(false);
  };

  const nextImage = () => {
    console.log('Next image clicked');
    setCurrentImageIndex((prev) => (prev + 1) % imageUrls.length);
  };

  const previousImage = () => {
    console.log('Previous image clicked');
    setCurrentImageIndex((prev) => (prev - 1 + imageUrls.length) % imageUrls.length);
  };

  return (
    <div className="p-4 flex flex-col items-start gap-4">
      <table className="w-full text-sm">
        <tbody>
          <tr>
            <td className="px-4 py-2">
              <strong>Camera Username:</strong> {record?.username}
            </td>
            <td className="px-4 py-2">
              <strong>IP Address:</strong> {record?.ip_address}
            </td>
            <td className="px-4 py-2">
              <strong>Camera ID:</strong> {record?.id}
            </td>
          </tr>
        </tbody>
      </table>

      {/* Image Display */}
      <Card className="inline-block p-4">
        {isLoading ? (
          <div className="text-center">Loading images...</div>
        ) : imageUrls.length > 0 ? (
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2">
              {imageUrls.length > 1 && (
                <Button 
                  onClick={previousImage} 
                  variant="secondary"
                  size="icon"
                  className="bg-white hover:bg-gray-100 shadow-md h-6 w-6 flex-shrink-0"
                >
                  <ChevronLeft className="h-3 w-3" />
                </Button>
              )}
              
              <div 
                style={{ width: '150px', height: '150px', maxWidth: '150px', maxHeight: '150px' }} 
                className="relative overflow-hidden rounded-lg border border-gray-200 cursor-pointer"
                onClick={() => setIsDialogOpen(true)}
              >
                <div className="relative h-full">
                  <img 
                    src={imageUrls[currentImageIndex]} 
                    alt={`Real Run Photo ${currentImageIndex + 1}`}
                    style={{ width: '150px', height: '150px', objectFit: 'cover' }}
                    className="w-full h-full"
                    onError={(e) => console.error('Image loading error:', e)}
                    onLoad={(e) => {
                      const img = e.target as HTMLImageElement;
                      console.log('Loaded image dimensions:', img.width, 'x', img.height);
                    }}
                  />
                </div>
              </div>

              {imageUrls.length > 1 && (
                <Button 
                  onClick={nextImage} 
                  variant="secondary"
                  size="icon"
                  className="bg-white hover:bg-gray-100 shadow-md h-6 w-6 flex-shrink-0"
                >
                  <ChevronRight className="h-3 w-3" />
                </Button>
              )}        
            </div>
            {imageUrls.length > 1 && (
              <div className="flex justify-center">
                <span className="text-white bg-black px-2 py-1 rounded-full test-xs- font-medium shadow-lg">
                  {currentImageIndex + 1} / {imageUrls.length}
                </span>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center text-gray-500">No images available</div>
        )}
      </Card>  

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-[90vw] max-h-[90vh]">
          <DialogHeader className="flex flex-row items-center justify-center gap-6">
            {imageUrls.length > 1 ? (
              <Button 
                onClick={previousImage} 
                variant="secondary"
                className="bg-black hover:bg-gray-800 shadow-md h-10 w-[50px] flex items-center justify-center"
              >
                <ChevronLeft className="h-6 w-6 text-white" />
              </Button>
            ) : (
              <div className="w-[50px]" /> /* Spacer for alignment */
            )}
            <DialogTitle className="mx-4">
              Image {currentImageIndex + 1} of {imageUrls.length}
            </DialogTitle>
            {imageUrls.length > 1 ? (
              <Button 
                onClick={nextImage} 
                variant="secondary"
                className="bg-black hover:bg-gray-800 shadow-md h-10 w-[50px] flex items-center justify-center"
              >
                <ChevronRight className="h-6 w-6 text-white" />
              </Button>
            ) : (
              <div className="w-[50px]" /> /* Spacer for alignment */
            )}
          </DialogHeader>
          <div className="relative w-full flex justify-center items-center">
            <img
              src={imageUrls[currentImageIndex]}
              alt={`Full size photo ${currentImageIndex + 1}`}
              className="max-w-full max-h-[70vh] object-contain"
            />
          </div>
          <DialogFooter className="w-full">
            {photos && photos[currentImageIndex] && (
              <DeleteButton
                record={{ id: photos[currentImageIndex].id.toString() }}
                onDelete={handlePhotoDelete}
              />
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}; 