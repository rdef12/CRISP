import { Button } from "@/components/ui/button";
import { useGetList, useRecordContext } from "react-admin";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Card } from "@/components/ui/card";

interface Photo {
  id: number;
  photo: string;
}

export const ShowRealRunPhoto = () => {
  const { beamRunId } = useParams();
  const [imageUrls, setImageUrls] = useState<string[]>([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const record = useRecordContext();
  
  const { data: photos, isLoading } = useGetList(
    `photo/beam-run/real/${beamRunId}/camera/${record?.id}`,
  );

  useEffect(() => {
    console.log('Photos data:', photos);
    if (photos) {
      const urls = photos.map((photo: Photo) => `data:image/jpeg;base64,${photo.photo}`);
      console.log('Generated URLs:', urls);
      console.log('Number of images:', urls.length);
      setImageUrls(urls);
    }
  }, [photos]);

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
            
            <div style={{ width: '150px', height: '150px', maxWidth: '150px', maxHeight: '150px' }} className="relative overflow-hidden rounded-lg border border-gray-200">
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
                {imageUrls.length > 1 && (
                  <div className="absolute bottom-1 left-0 right-0 flex justify-center z-10">
                    <span className="text-white bg-black px-2 py-1 rounded-full text-xs font-medium shadow-lg">
                      {currentImageIndex + 1} / {imageUrls.length}
                    </span>
                  </div>
                )}
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
        ) : (
          <div className="text-center text-gray-500">No images available</div>
        )}
      </Card>  

    </div>
  );
}; 