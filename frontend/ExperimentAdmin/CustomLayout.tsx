import { Layout, LayoutProps, Sidebar, SidebarProps } from "react-admin";

const MySidebar: React.FC<SidebarProps> = (props) => <Sidebar {...props} hidden>{props.children ?? null}</Sidebar>;


// Custom layout without the App Bar
const CustomAdminLayout = (props: LayoutProps) => {
  return <Layout {...props} appBar={() => null} sidebar={MySidebar} />;
};

export default CustomAdminLayout;