import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { useGetList } from "react-admin";

interface TestSetting {
  id: number;
  camera_settings_id: number;
  gain: number;
  frame_rate: number;
  lens_position: number;
  is_optimal?: boolean;
}

interface ImageOverlayCarouselProps {
  selectedSetting: TestSetting | null;
}

interface Photo {
  id: number;
  photo: string;
}

export const ImageOverlayCarousel = ({ selectedSetting }: ImageOverlayCarouselProps) => {
  const { beamRunId } = useParams();
  const [imageUrls, setImageUrls] = useState<string[]>([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const { data: imageOverlays, isLoading } = useGetList(
    `photo/beam-run/test/${beamRunId}/camera-settings/${selectedSetting?.camera_settings_id}`,
  );

  useEffect(() => {
    console.log('Image Data:', imageOverlays);
    if (imageOverlays) {
      const urls = imageOverlays.map((photo: Photo) => `data:image/jpeg;base64,${photo.photo}`);
      console.log('Generated URLs:', urls);
      console.log('Number of images:', urls.length);      setImageUrls(urls);
    } else {
      console.log('No image data available');
    }
  }, [imageOverlays]);

  const nextImage = () => {
    console.log('Next image clicked');
    setCurrentImageIndex((prev) => (prev + 1) % imageUrls.length);
  };

  const previousImage = () => {
    console.log('Previous image clicked');
    setCurrentImageIndex((prev) => (prev - 1 + imageUrls.length) % imageUrls.length);
  };
  return (
    <div className="w-full">
        {isLoading ? (
          <div className="text-center">Loading images...</div>
        ) : imageUrls.length > 0 ? (
          <div className="relative w-full overflow-hidden rounded-lg border border-gray-200">
            <div className="relative">
              <img 
                src={imageUrls[currentImageIndex]} 
                alt={`Real Run Photo ${currentImageIndex + 1}`}
                className="w-full object-contain"
                onError={(e) => console.error('Image loading error:', e)}
              />
              {imageUrls.length > 1 && (
                <div className="absolute inset-0 flex items-center justify-between p-4 z-10">
                  <Button 
                    onClick={previousImage} 
                    variant="secondary"
                    size="icon"
                    className="bg-white hover:bg-gray-100 shadow-md"
                  >
                    <ChevronLeft className="h-6 w-6" />
                  </Button>
                  <Button 
                    onClick={nextImage} 
                    variant="secondary"
                    size="icon"
                    className="bg-white hover:bg-gray-100 shadow-md"
                  >
                    <ChevronRight className="h-6 w-6" />
                  </Button>
                </div>
              )}
              {imageUrls.length > 1 && (
                <div className="absolute bottom-4 left-0 right-0 flex justify-center z-10">
                  <span className="text-white bg-black px-4 py-2 rounded-full text-sm font-medium shadow-lg">
                    {currentImageIndex + 1} / {imageUrls.length}
                  </span>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center text-gray-500">No images available</div>
        )}

    </div>

  )
}