import * as React from "react";
import { useLocation } from "react-router-dom";
import { useGetOne } from "react-admin";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";

interface BreadcrumbItem {
  label: string;
  href: string;
}

export const Breadcrumbs = () => {
  const location = useLocation();
  const pathnames = location.pathname.replace('#', '').split("/").filter((x) => x);

  // Get beam run data if we're in a beam run
  const beamRunId = pathnames.includes('beam-run') ? pathnames[pathnames.indexOf('beam-run') + 2] : null;
  const { data: beamRunData, isPending: isBeamRunPending } = useGetOne(
    'beam-run/just-one',
    { id: beamRunId },
    { enabled: !!beamRunId }
  );

  // Group the path segments into logical sections
  const getBreadcrumbItems = () => {
    const items: BreadcrumbItem[] = [];
    
    // Always show Experiments
    items.push({
      label: 'Experiments',
      href: `/${pathnames[0]}`
    });

    // If we have an experiment ID, show it
    if (pathnames.length > 1) {
      items.push({
        label: `Experiment ${pathnames[1]}`,
        href: `/${pathnames[0]}/${pathnames[1]}`
      });
    }

    // If we're in a beam run section
    if (pathnames.includes('beam-run')) {
      const beamRunIndex = pathnames.indexOf('beam-run');
      // Skip the 'beam-run' segment and go directly to the type (real/test)
      if (pathnames.length > beamRunIndex + 2) {
        const runType = pathnames[beamRunIndex + 1];
        const beamRunNumber = isBeamRunPending ? '...' : beamRunData?.beam_run_number;
        items.push({
          label: `Run ${beamRunNumber} - ${runType.charAt(0).toUpperCase() + runType.slice(1)}`,
          href: `/${pathnames.slice(0, beamRunIndex + 3).join('/')}`
        });
      }

      // If we're in take-data
      if (pathnames.includes('take-data')) {
        items.push({
          label: 'Take Data',
          href: `/${pathnames.join('/')}`
        });
      }
    }

    return items;
  };

  const breadcrumbs = getBreadcrumbItems();
  const handleNavigation = (path: string) => {
    window.location.hash = path;
  };
  // Only show breadcrumbs if we're past the experiments level
  if (pathnames.length <= 1) return null;

  return (
    <div className="p-4 bg-muted border-b">
      <Breadcrumb>
        <BreadcrumbList>
          {breadcrumbs.map((item, index) => (
            <React.Fragment key={item.href}>
              <BreadcrumbItem>
                {index === breadcrumbs.length - 1 ? (
                  <BreadcrumbPage>{item.label}</BreadcrumbPage>
                ) : (
                  <BreadcrumbLink
                    onClick={() => handleNavigation(item.href)}
                    className="cursor-pointer"
                  >
                    {item.label}
                  </BreadcrumbLink>
                )}
              </BreadcrumbItem>
              {index < breadcrumbs.length - 1 && <BreadcrumbSeparator />}
            </React.Fragment>
          ))}
        </BreadcrumbList>
      </Breadcrumb>
    </div>
  );
}; 