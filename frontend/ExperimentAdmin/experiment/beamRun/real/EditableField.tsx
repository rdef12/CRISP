// import { useState } from "react";
// import { useRecordContext } from "react-admin";
// import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
// import { Button } from "@/components/ui/button";
// import { Input } from "@/components/ui/input";
// import { Label } from "@/components/ui/label";

// interface EditableFieldProps {
//   source: string;
//   label?: string;
//   onSave: (newValue: string) => void;
// }

// export const EditableField = ({ source, label, onSave }: EditableFieldProps) => {
//   const record = useRecordContext();
//   const [isDialogOpen, setIsDialogOpen] = useState(false);
//   const [editValue, setEditValue] = useState(record?.[source] || '');

//   const handleCloseDialog = () => {
//     setIsDialogOpen(false);
//     setEditValue(record?.[source] || '');
//   };

//   const handleSave = () => {
//     onSave(editValue);
//     handleCloseDialog();
//   };

//   return (
//     <>
//       <Dialog open={isDialogOpen} onOpenChange={handleCloseDialog}>
//         <DialogContent>
//           <DialogHeader>
//             <DialogTitle>Edit {label || source}</DialogTitle>
//           </DialogHeader>
//           <div className="space-y-4 py-4">
//             <div className="space-y-2">
//               <Label htmlFor="value">{label || source}</Label>
//               <Input
//                 id="value"
//                 value={editValue}
//                 onChange={(e) => setEditValue(e.target.value)}
//               />
//             </div>
//             <div className="flex justify-end space-x-2">
//               <Button variant="outline" onClick={handleCloseDialog}>
//                 Cancel
//               </Button>
//               <Button onClick={handleSave}>
//                 Save
//               </Button>
//             </div>
//           </div>
//         </DialogContent>
//       </Dialog>

//       <Button
//         variant="ghost"
//         className="h-auto p-0 hover:bg-transparent"
//         onClick={() => setIsDialogOpen(true)}
//       >
//         {record?.[source]}
//       </Button>
//     </>
//   );
// }; 


// const handleFieldSave = (source: string) => (newValue: string) => {
//   // Here you would typically make an API call to update the value
//   console.log(`Updating ${source} to:`, newValue);
//   setRefreshTrigger(!refreshTrigger);
// };


// <EditableField source="ip_address" label="IP Address" onSave={handleFieldSave('ip_address')} />
