import { Checkbox } from "@/components/ui/checkbox";
import { CheckboxOption } from "./types";

interface GridTransformationProps {
  checkedStates: {
    horizontal_flip: boolean;
    vertical_flip: boolean;
    swap_axes: boolean;
  };
  onCheckboxChange: (option: CheckboxOption) => void;
}

export const GridTransformation = ({ checkedStates, onCheckboxChange }: GridTransformationProps) => {
  return (
    <div className="flex flex-row items-center justify-center space-x-8">
      <div className="flex items-center space-x-2">
        <Checkbox 
          id="horizontal_flip" 
          checked={checkedStates.horizontal_flip}
          onCheckedChange={() => onCheckboxChange('horizontal_flip')}
        />
        <label
          htmlFor="horizontal_flip"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          Horizontal Flip
        </label>
      </div>
      <div className="flex items-center space-x-2">
        <Checkbox 
          id="vertical_flip" 
          checked={checkedStates.vertical_flip}
          onCheckedChange={() => onCheckboxChange('vertical_flip')}
        />
        <label
          htmlFor="vertical_flip"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          Vertical Flip
        </label>
      </div>
      <div className="flex items-center space-x-2">
        <Checkbox 
          id="swap_axes" 
          checked={checkedStates.swap_axes}
          onCheckedChange={() => onCheckboxChange('swap_axes')}
        />
        <label
          htmlFor="swap_axes"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          Swap Axes
        </label>
      </div>
    </div>
  );
}