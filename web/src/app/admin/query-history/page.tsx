"use client";

import { AdminPageTitle } from "@/components/admin/Title";
import { QueryHistoryTable } from "@/app/admin/query-history/QueryHistoryTable";
import { SvgServer } from "@opal/icons";

export default function QueryHistoryPage() {
  return (
    <>
      <AdminPageTitle title="Query History" icon={SvgServer} />
      <QueryHistoryTable />
    </>
  );
}
