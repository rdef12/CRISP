import { Setup, setup_columns } from "./columns"
import { DataTable } from "./data-table"
import AddNewSetup from "./add_new_setup"

const getSetups = async (): Promise<Setup[]> => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND}/get_setups`, {
        method: "GET",
      });
      return await response.json();
    } catch (error) {
      console.error("Error fetching setups:", error);
      return [];
    }
  }
 

// export async function getServerSideProps() {
//   try {
//     const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND}/get_setups`);
//     const setups = await response.json();
//     return { props: { setups } };
//   } catch (error) {
//     console.error("Error fetching setups:", error);
//     return { props: { setups: [] } };
//   }
// }


export default async function SetupHubPage() {
  const setups = await getSetups()
  return (
    <div>
      <div>
        <AddNewSetup />
      </div>
      <div className="container mx-auto py-10">
        <DataTable columns={setup_columns} data={setups} />
      </div>
    </div>
  )
}