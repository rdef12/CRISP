import { HomographyPlane } from "./HomographyCalibration";

interface ShowHomographyCalibrationImageProps {
  imageUrl: string;
}

export const ShowHomographyCalibrationImage = ({ imageUrl }: ShowHomographyCalibrationImageProps) => {
  console.log('Image URL received:', imageUrl); // Debug log

  if (!imageUrl) return <div>No image available</div>;

  return (
    <div className="calibration-image-container">
      <img 
        src={imageUrl} 
        alt="Homography calibration result"
        style={{ 
          maxWidth: '100%', 
          height: 'auto',
          border: '1px solid #ccc', // Add border to make image container visible
          padding: '10px',
          backgroundColor: '#f5f5f5'
        }}
        onError={(e) => {
          console.error('Image failed to load:', e);
          const target = e.target as HTMLImageElement;
          target.style.display = 'none';
        }}
      />
    </div>
  );
}