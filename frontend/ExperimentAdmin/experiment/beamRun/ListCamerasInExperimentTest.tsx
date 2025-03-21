import { Datagrid, Identifier, List, RaRecord, TextField, useShowController } from "react-admin";
import { useParams } from "react-router-dom";
import { CreateTestSettings } from "./CreateTestSettings";
import { useState } from "react";
import { Dialog, DialogTrigger } from "@radix-ui/react-dialog";
import { Button } from "@/components/ui/button";

export const ListCamerasInExperimentTest = () => {
  const { experimentId } = useParams();
  const [dialogIsOpen, setDialogIsOpen] = useState(false);
  const [selectedCamera, setSelectedCamera] = useState(null);

  // const { data, isPending, resource } = useListController({ resource: `experiment/cameras/${experimentId}` });
  const { isPending, resource, record } = useShowController({ resource: `experiment`, id: experimentId, queryOptions: { meta: { setup: "setup", cameras: "cameras" }}})
  // const redirectOnRowClick = (id: Identifier, resource: string, record: RaRecord) => ()
  

  // const handleRowClick = (id, resource, record) => {
  //   setSelectedCamera(record);
  //   setIsOpen(true);
  // };
  const openDialog = () => {
    <DialogTrigger asChild>

    </DialogTrigger>
    }

  if (isPending) return null;
  return (
    <List resource={resource} >
      <Datagrid data={record.cameras} onClick={openDialog} >
        <TextField source="username" />
        <TextField source="ip_address" />
      </Datagrid>
    </List>
  )
}

export const ListCamerasInExperiment = () => {
  const { experimentId } = useParams();
  // const { data, isPending, resource } = useListController({ resource: `experiment/cameras/${experimentId}` });
  const { isPending, resource, record } = useShowController({ resource: `experiment`, id: experimentId, queryOptions: { meta: { setup: "setup", cameras: "cameras" }}})
  // const redirectOnRowClick = (id: Identifier, resource: string, record: RaRecord) => ()

  if (isPending) return null;
  // CURRENTLY BUTTON AND EXPANDABLE FOR EXAMPLE PURPOSES
  return (
    <List resource={resource} >
      <Datagrid data={record.cameras} expand={<div>I have expanded</div>} expandSingle bulkActionButtons={false}>
        <TextField source="username" />
        <TextField source="ip_address" />
        <Button> See Me </Button>
      </Datagrid>
    </List>
  )
}