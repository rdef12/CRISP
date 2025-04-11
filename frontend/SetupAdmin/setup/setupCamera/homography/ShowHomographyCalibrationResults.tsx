import { useParams } from "react-router-dom";
import { ShowHomographyCalibrationImage } from "./ShowHomographyCalibrationImage"
import { ShowHomographyCalibrationSuccess } from "./ShowHomographyCalibrationSuccess"
import { useDataProvider, DataProvider } from "react-admin";
import { HomographyPlane } from "./HomographyCalibration";
import { useState, useEffect, useRef } from "react";
import { GridTransformation } from "./GridTransformation";
import { SaveHomographyButton } from "./SaveHomographyButton";

type CheckboxOption = 'horizontal_flip' | 'vertical_flip' | 'swap_axes';

interface HomographyPhotoData {
  photo: string;
  status?: boolean;
  message?: string;
}

interface CustomDataProvider extends DataProvider {
  getHomographyPhoto: (plane: string, id: string, params: Record<string, string>) => Promise<{ data: HomographyPhotoData }>;
}

const useGetOneHomographyPhoto = (plane: HomographyPlane, id: string, queryParams: Record<string, string>) => {
  const dataProvider = useDataProvider() as unknown as CustomDataProvider;
  const [data, setData] = useState<HomographyPhotoData | null>(null);
  const [isPending, setIsPending] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    try {
      setIsPending(true);
      const result = await dataProvider.getHomographyPhoto(plane, id, queryParams);
      setData(result.data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsPending(false);
    }
  };

  return { data, isPending, error, refetch: fetchData };
};

interface ShowHomographyCalibrationResultsProps {
  plane: HomographyPlane;
  imageTaken: boolean;
  onImageLoaded: () => void;
}

export const ShowHomographyCalibrationResults = ({ plane, imageTaken, onImageLoaded }: ShowHomographyCalibrationResultsProps) => {
  const { setupCameraId } = useParams();
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const initialMount = useRef(true);
  
  const [checkedStates, setCheckedStates] = useState({
    horizontal_flip: false,
    vertical_flip: false,
    swap_axes: false,
  });

  const handleCheckboxChange = (option: CheckboxOption) => {
    setCheckedStates(prev => ({
      ...prev,
      [option]: !prev[option]
    }));
  };
  
  console.log('Component rendered with:', { plane, setupCameraId, imageTaken });
  
  const { data, isPending, error, refetch } = useGetOneHomographyPhoto(
    plane,
    setupCameraId!,
    {
      horizontal_flip: checkedStates.horizontal_flip.toString(),
      vertical_flip: checkedStates.vertical_flip.toString(),
      swap_axes: checkedStates.swap_axes.toString()
    }
  );

  // Fetch on initial mount
  useEffect(() => {
    if (initialMount.current) {
      console.log('Initial mount, fetching image');
      refetch();
      initialMount.current = false;
    }
  }, []);

  // Refetch when image is taken or checkbox states change
  useEffect(() => {
    if (imageTaken || !initialMount.current) {
      console.log('New image taken or checkbox state changed, refetching');
      refetch();
    }
  }, [imageTaken, checkedStates]);

  useEffect(() => {
    if (data?.photo) {
      const url = `data:image/jpeg;base64,${data.photo}`;
      setImageUrl(url);
      onImageLoaded();
    } else {
      setImageUrl(null);
    }
  }, [data?.photo, onImageLoaded]);


  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <GridTransformation 
        checkedStates={checkedStates}
        onCheckboxChange={handleCheckboxChange}
      />
      <div style={{ minHeight: '400px', position: 'relative' }}>
        {error ? (
          <div>Error loading calibration results</div>
        ) : isPending ? (
          <div style={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            right: 0, 
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.1)',
            borderRadius: '0.5rem',
            animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
          }} />
        ) : imageUrl ? (
          <ShowHomographyCalibrationImage imageUrl={imageUrl} />
        ) : (
          <div>No calibration image available</div>
        )}
      </div>
      {data?.status != null && data?.message != null && (
        <ShowHomographyCalibrationSuccess status={data.status} message={data.message} />
      )}
      {data?.status === true && (
        <SaveHomographyButton
          plane={plane}
          horizontal_flip={checkedStates.horizontal_flip}
          vertical_flip={checkedStates.vertical_flip}
          swap_axes={checkedStates.swap_axes}
         />
      )}
    </div>
  )
}