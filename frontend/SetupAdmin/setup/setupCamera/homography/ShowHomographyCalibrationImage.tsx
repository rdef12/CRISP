import { Card } from "@/components/ui/card";
import { HomographyPlane } from "./HomographyCalibration";

interface ShowHomographyCalibrationImageProps {
  imageUrl: string;
}

export const ShowHomographyCalibrationImage = ({ imageUrl }: ShowHomographyCalibrationImageProps) => {
  if (!imageUrl) return <div>No image available</div>;

  return (
    <Card>
      <div className="calibration-image-container" style={{ 
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '1rem'
      }}>
        <img 
          src={imageUrl} 
          alt="Homography calibration result"
          style={{ 
            maxWidth: '600px', 
            height: 'auto',
            display: 'block'
          }}
          onError={(e) => {
            console.error('Image failed to load:', e);
            const target = e.target as HTMLImageElement;
            target.style.display = 'none';
          }}
        />
      </div>
    </Card>
  );
}