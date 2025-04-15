// import { useEffect, useState } from 'react';
// import { Progress } from "@/components/ui/progress"

// interface TimerProps {
//   duration: number;
// }

// export const Timer = ({ duration }: TimerProps) => {
//   const [elapsedTime, setElapsedTime] = useState(0);

//   // // Easing function that starts slowing down at 50% progress and then slowly increments from 90 to 99
//   // const getEasedProgress = (progress: number) => {
//   //   if (progress < 0.3) {
//   //     return 12 * progress * progress * progress; // Very fast initial progress
//   //   } else if (progress < 0.9) {
//   //     return 0.5 + Math.pow((progress - 0.3) / 0.7, 3) * 0.5; // Slower progress until 90%
//   //   } else {
//   //     // Once we reach 90%, slowly increment by 1 every 10% of remaining time
//   //     const remainingProgress = (progress - 0.9) / 0.3;
//   //     return 0.9 + Math.min(remainingProgress * 9, 0.09); // Add up to 9% more, slowly
//   //   }
//   // };

//   const customEase = (x: number) => {
//     if (x < 0.3) {
//       return Math.pow(x / 0.3, 0.5) * 0.5;
//     } else if (x < 0.9) {
//       return 0.5 + (Math.pow((x - 0.3) / 0.6, 2) * 0.4);
//     } else {
//       return 0.9 + (x - 0.9) * 0.1;
//     }
//   };

//   useEffect(() => {
//     const startTime = Date.now();
//     const interval = setInterval(() => {
//       const currentTime = Date.now();
//       setElapsedTime(currentTime - startTime);
//     }, 10);

//     return () => clearInterval(interval);
//   }, []);

//   const unrounded_seconds = elapsedTime / 1000;
//   const rawProgress = Math.min(unrounded_seconds / duration, 1);
//   const easedProgress = customEase(rawProgress) * 100;
//   const seconds = Math.floor(elapsedTime / 1000);
//   const milliseconds = Math.floor((elapsedTime % 1000) / 10);
//   // Calculate eased time display
//   // const easedSeconds = Math.floor((easedProgress / 100) * duration);
//   // const easedMilliseconds = Math.floor(((easedProgress / 100) * duration - easedSeconds) * 100);

//   return (
//     <div>
//       <div className="text-lg font-semibold">
//         Time elapsed: {seconds}.{milliseconds.toString().padStart(2, '0')} seconds
//       </div>
//       <div className="flex items-center gap-2">
//         <Progress value={Math.min(easedProgress, 99)} />
//         <span className="text-sm font-medium">{Math.min(Math.floor(easedProgress), 99)}%</span>
//       </div>
//     </div>
//   );
// }; 
import { useEffect, useState } from 'react';
import { Progress } from '@/components/ui/progress';

export const Timer = ({ duration }: { duration: number }) => {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [extraProgress, setExtraProgress] = useState(0); // For 90% → 99%

  // Your custom easing function
  const customEase = (x: number) => {
    if (x < 0.3) {
      return Math.pow((x) / 0.3, 0.5) * 0.5;
    } else if (x < 0.9) {
      return 0.5 + (Math.pow((x - 0.3) / 0.6, 2) * 0.4);
    } else {
      return 0.9; // freeze easing at 90%, extra handled separately
    }
  };

  useEffect(() => {
    const startTime = Date.now();
    const interval = setInterval(() => {
      const now = Date.now();
      setElapsedTime(now - startTime);
    }, 10);
    return () => clearInterval(interval);
  }, []);

  const progressDuration = duration * 1.5

  const unrounded_seconds = elapsedTime / 1000;
  const linearProgress = Math.min(unrounded_seconds / progressDuration, 1);
  const eased = customEase(linearProgress);
  const progressBefore90 = Math.min(eased * 100, 90);

  // Start slow progression from 90 → 99 once eased hits 90
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    if (progressBefore90 >= 90 && extraProgress < 9) {
      interval = setInterval(() => {
        setExtraProgress((prev) => Math.min(prev + 0.1, 9));
      }, 300); // controls speed of 90 → 99
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [progressBefore90, extraProgress]);

  const totalProgress = progressBefore90 + extraProgress;
  const displayProgress = Math.min(totalProgress, 99);

  const seconds = Math.floor(unrounded_seconds);
  const milliseconds = Math.floor((elapsedTime % 1000) / 10);

  return (
    <div>
      <div className="text-lg font-semibold">
        Time elapsed: {seconds}.{milliseconds.toString().padStart(2, '0')} seconds
      </div>
      <div className="flex items-center gap-2">
        <Progress value={displayProgress} />
        <span className="text-sm font-medium">
          {Math.floor(displayProgress)}%
        </span>
      </div>
    </div>
  );
};