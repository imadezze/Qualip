"use client";

import Separator from "@/refresh-components/Separator";
import {
  Table,
  TableHead,
  TableRow,
  TableBody,
  TableCell,
  TableHeader,
} from "@/components/ui/table";
import Text from "@/refresh-components/texts/Text";
import InputSelect from "@/refresh-components/inputs/InputSelect";
import { ThreeDotsLoader } from "@/components/Loading";
import { ChatSessionMinimal } from "@/app/admin/query-history/types";
import { timestampToReadableDate } from "@/lib/dateUtils";
import { useCallback, useState } from "react";
import { Feedback } from "@/lib/types";
import {
  DateRange,
  AdminDateRangeSelector,
} from "@/components/dateRangeSelectors/AdminDateRangeSelector";
import { PageSelector } from "@/components/PageSelector";
import { useRouter } from "next/navigation";
import { FeedbackBadge } from "@/app/admin/query-history/FeedbackBadge";
import CardSection from "@/components/admin/CardSection";
import usePaginatedFetch from "@/hooks/usePaginatedFetch";
import { ErrorCallout } from "@/components/ErrorCallout";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  SvgMinusCircle,
  SvgThumbsDown,
  SvgThumbsUp,
  SvgMinus,
  SvgEye,
  SvgBubbleText,
  SvgSettings,
} from "@opal/icons";
import Button from "@/refresh-components/buttons/Button";

const ITEMS_PER_PAGE = 20;
const PAGES_PER_BATCH = 2;

type ViewMode = "preview" | "chat";

type ColumnKey =
  | "first_user_message"
  | "first_ai_message"
  | "feedback"
  | "user"
  | "assistant"
  | "date";

const ALL_COLUMNS: { key: ColumnKey; label: string }[] = [
  { key: "first_user_message", label: "First User Message" },
  { key: "first_ai_message", label: "First AI Response" },
  { key: "feedback", label: "Feedback" },
  { key: "user", label: "User" },
  { key: "assistant", label: "Assistant" },
  { key: "date", label: "Date" },
];

const DEFAULT_COLUMNS: ColumnKey[] = [
  "first_user_message",
  "first_ai_message",
  "feedback",
  "user",
  "date",
];

async function shareChatSession(chatSessionId: string): Promise<boolean> {
  try {
    const response = await fetch(
      `/api/admin/chat-session-history/${chatSessionId}/share`,
      { method: "POST" }
    );
    return response.ok;
  } catch {
    return false;
  }
}

function QueryHistoryTableRow({
  chatSessionMinimal,
  viewMode,
  visibleColumns,
}: {
  chatSessionMinimal: ChatSessionMinimal;
  viewMode: ViewMode;
  visibleColumns: ColumnKey[];
}) {
  const router = useRouter();
  const [isSharing, setIsSharing] = useState(false);

  const handleClick = async () => {
    if (viewMode === "preview") {
      router.push(`/admin/query-history/${chatSessionMinimal.id}`);
    } else {
      setIsSharing(true);
      const success = await shareChatSession(chatSessionMinimal.id);
      if (success) {
        router.push(`/chat/shared/${chatSessionMinimal.id}`);
      } else {
        alert("Failed to share chat session");
        setIsSharing(false);
      }
    }
  };

  return (
    <TableRow
      className="hover:bg-accent-background cursor-pointer select-none"
      onClick={handleClick}
    >
      {visibleColumns.includes("first_user_message") && (
        <TableCell>
          <Text className="whitespace-normal line-clamp-3 max-w-[300px]">
            {isSharing
              ? "Sharing..."
              : chatSessionMinimal.first_user_message ||
                chatSessionMinimal.name ||
                "-"}
          </Text>
        </TableCell>
      )}
      {visibleColumns.includes("first_ai_message") && (
        <TableCell>
          <Text className="whitespace-normal line-clamp-3 max-w-[300px]">
            {chatSessionMinimal.first_ai_message || "-"}
          </Text>
        </TableCell>
      )}
      {visibleColumns.includes("feedback") && (
        <TableCell>
          <FeedbackBadge feedback={chatSessionMinimal.feedback_type} />
        </TableCell>
      )}
      {visibleColumns.includes("user") && (
        <TableCell>
          <Text className="truncate max-w-[200px]">
            {chatSessionMinimal.user_email || "-"}
          </Text>
        </TableCell>
      )}
      {visibleColumns.includes("assistant") && (
        <TableCell>
          <Text className="truncate max-w-[150px]">
            {chatSessionMinimal.assistant_name || "Unknown"}
          </Text>
        </TableCell>
      )}
      {visibleColumns.includes("date") && (
        <TableCell>
          <Text className="whitespace-nowrap">
            {timestampToReadableDate(chatSessionMinimal.time_created)}
          </Text>
        </TableCell>
      )}
    </TableRow>
  );
}

function SelectFeedbackType({
  value,
  onValueChange,
}: {
  value: Feedback | "all";
  onValueChange: (value: Feedback | "all") => void;
}) {
  return (
    <div>
      <Text as="p" className="my-auto mr-2 font-medium mb-1">
        Feedback Type
      </Text>
      <div className="max-w-sm space-y-6">
        <InputSelect
          value={value}
          onValueChange={onValueChange as (value: string) => void}
        >
          <InputSelect.Trigger />

          <InputSelect.Content>
            <InputSelect.Item value="all" icon={SvgMinusCircle}>
              Any
            </InputSelect.Item>
            <InputSelect.Item value="like" icon={SvgThumbsUp}>
              Like
            </InputSelect.Item>
            <InputSelect.Item value="dislike" icon={SvgThumbsDown}>
              Dislike
            </InputSelect.Item>
            <InputSelect.Item value="mixed" icon={SvgMinus}>
              Mixed
            </InputSelect.Item>
          </InputSelect.Content>
        </InputSelect>
      </div>
    </div>
  );
}

function SelectViewMode({
  value,
  onValueChange,
}: {
  value: ViewMode;
  onValueChange: (value: ViewMode) => void;
}) {
  return (
    <div>
      <Text as="p" className="my-auto mr-2 font-medium mb-1">
        View Mode
      </Text>
      <div className="max-w-sm space-y-6">
        <InputSelect
          value={value}
          onValueChange={onValueChange as (value: string) => void}
        >
          <InputSelect.Trigger />

          <InputSelect.Content>
            <InputSelect.Item value="preview" icon={SvgEye}>
              Preview Details
            </InputSelect.Item>
            <InputSelect.Item value="chat" icon={SvgBubbleText}>
              View in Chat
            </InputSelect.Item>
          </InputSelect.Content>
        </InputSelect>
      </div>
    </div>
  );
}

function ColumnSelector({
  visibleColumns,
  onToggleColumn,
}: {
  visibleColumns: ColumnKey[];
  onToggleColumn: (column: ColumnKey) => void;
}) {
  return (
    <div>
      <Text as="p" className="my-auto mr-2 font-medium mb-1">
        Columns
      </Text>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button secondary leftIcon={SvgSettings}>
            Select Columns
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56" align="start">
          <DropdownMenuLabel>Visible Columns</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {ALL_COLUMNS.map((column) => (
            <DropdownMenuCheckboxItem
              key={column.key}
              checked={visibleColumns.includes(column.key)}
              onCheckedChange={() => onToggleColumn(column.key)}
            >
              {column.label}
            </DropdownMenuCheckboxItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}

export function QueryHistoryTable() {
  const [dateRange, setDateRange] = useState<DateRange>(undefined);
  const [viewMode, setViewMode] = useState<ViewMode>("preview");
  const [visibleColumns, setVisibleColumns] =
    useState<ColumnKey[]>(DEFAULT_COLUMNS);
  const [filters, setFilters] = useState<{
    feedback_type?: Feedback | "all";
    start_time?: string;
    end_time?: string;
  }>({});

  const {
    currentPageData: chatSessionData,
    isLoading,
    error,
    currentPage,
    totalPages,
    goToPage,
  } = usePaginatedFetch<ChatSessionMinimal>({
    itemsPerPage: ITEMS_PER_PAGE,
    pagesPerBatch: PAGES_PER_BATCH,
    endpoint: "/api/admin/chat-session-history",
    filter: filters,
  });

  const onTimeRangeChange = useCallback((value: DateRange) => {
    setDateRange(value);

    if (value?.from && value?.to) {
      setFilters((prev) => ({
        ...prev,
        start_time: value.from.toISOString(),
        end_time: value.to.toISOString(),
      }));
    } else {
      setFilters((prev) => {
        const newFilters = { ...prev };
        delete newFilters.start_time;
        delete newFilters.end_time;
        return newFilters;
      });
    }
  }, []);

  const handleToggleColumn = (column: ColumnKey) => {
    setVisibleColumns((prev) => {
      if (prev.includes(column)) {
        // Don't allow removing all columns
        if (prev.length === 1) return prev;
        return prev.filter((c) => c !== column);
      }
      return [...prev, column];
    });
  };

  if (error) {
    return (
      <ErrorCallout
        errorTitle="Error fetching query history"
        errorMsg={error?.message}
      />
    );
  }

  return (
    <CardSection className="mt-8">
      <div className="flex flex-wrap gap-4 items-end">
        <SelectViewMode value={viewMode} onValueChange={setViewMode} />
        <SelectFeedbackType
          value={filters.feedback_type || "all"}
          onValueChange={(value) => {
            setFilters((prev) => {
              const newFilters = { ...prev };
              if (value === "all") {
                delete newFilters.feedback_type;
              } else {
                newFilters.feedback_type = value;
              }
              return newFilters;
            });
          }}
        />
        <AdminDateRangeSelector
          value={dateRange}
          onValueChange={onTimeRangeChange}
        />
        <ColumnSelector
          visibleColumns={visibleColumns}
          onToggleColumn={handleToggleColumn}
        />
      </div>
      <Separator />
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              {visibleColumns.includes("first_user_message") && (
                <TableHead>First User Message</TableHead>
              )}
              {visibleColumns.includes("first_ai_message") && (
                <TableHead>First AI Response</TableHead>
              )}
              {visibleColumns.includes("feedback") && (
                <TableHead>Feedback</TableHead>
              )}
              {visibleColumns.includes("user") && <TableHead>User</TableHead>}
              {visibleColumns.includes("assistant") && (
                <TableHead>Assistant</TableHead>
              )}
              {visibleColumns.includes("date") && <TableHead>Date</TableHead>}
            </TableRow>
          </TableHeader>
          {isLoading ? (
            <TableBody>
              <TableRow>
                <TableCell
                  colSpan={visibleColumns.length}
                  className="text-center"
                >
                  <ThreeDotsLoader />
                </TableCell>
              </TableRow>
            </TableBody>
          ) : (
            <TableBody>
              {chatSessionData?.map((chatSessionMinimal) => (
                <QueryHistoryTableRow
                  key={chatSessionMinimal.id}
                  chatSessionMinimal={chatSessionMinimal}
                  viewMode={viewMode}
                  visibleColumns={visibleColumns}
                />
              ))}
            </TableBody>
          )}
        </Table>
      </div>

      {chatSessionData && (
        <div className="mt-3 flex">
          <div className="mx-auto">
            <PageSelector
              totalPages={totalPages}
              currentPage={currentPage}
              onPageChange={goToPage}
            />
          </div>
        </div>
      )}
    </CardSection>
  );
}
