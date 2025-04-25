import { NavigationMenu, NavigationMenuList, NavigationMenuItem,
  NavigationMenuLink, navigationMenuTriggerStyle } from "@/components/ui/navigation-menu";
import Link from "next/link";

export function NavigationBar() {
  return (
  // {/* Navigation Container with Logo on the Left */}
  <div className="flex items-center justify-between bg-gray-200 p-4">
    {/* Logo */}
    <div className="flex items-center space-x-2">
      <img src="/images/logo.png" alt="CRISP Logo" className="h-8" />
    </div>

    {/* Centered Navbar */}
    <div className="flex justify-center flex-grow">
      <NavigationMenu className="text-2xl">
        <NavigationMenuList className="flex space-x-2 justify-center">
          <NavigationMenuItem>
            <Link href="/" legacyBehavior passHref>
              <NavigationMenuLink className={`${navigationMenuTriggerStyle()} text-2xl bg-zinc-300`}>
                Home
              </NavigationMenuLink>
            </Link>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <Link href="/experiments" legacyBehavior passHref>
              <NavigationMenuLink className={`${navigationMenuTriggerStyle()} text-2xl`}>
                Experiments
              </NavigationMenuLink>
            </Link>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <Link href="/setup_hub" legacyBehavior passHref>
              <NavigationMenuLink className={`${navigationMenuTriggerStyle()} text-2xl`}>
                Setups
              </NavigationMenuLink>
            </Link>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <Link href="/docs" legacyBehavior passHref>
              <NavigationMenuLink className={`${navigationMenuTriggerStyle()} text-2xl`}>
                Documentation
              </NavigationMenuLink>
            </Link>
          </NavigationMenuItem>
          {/* <NavigationMenuItem>
            <Link href="/streams" legacyBehavior passHref>
              <NavigationMenuLink className={`${navigationMenuTriggerStyle()} text-2xl`}>
                Streams
              </NavigationMenuLink>
            </Link>
          </NavigationMenuItem> */}
          <NavigationMenuItem>
            <Link href="/image_testing" legacyBehavior passHref>
              <NavigationMenuLink className={`${navigationMenuTriggerStyle()} text-2xl`}>
                Image Testing
              </NavigationMenuLink>
            </Link>
          </NavigationMenuItem>
        </NavigationMenuList>
      </NavigationMenu>
    </div>
  </div>
  )
}
