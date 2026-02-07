import { INTERNAL_URL } from "@/lib/constants";
import { NextRequest, NextResponse } from "next/server";

/* NextJS is annoying and makes use use a separate function for
each request type >:( */

export async function GET(
  request: NextRequest,
  props: { params: Promise<{ path: string[] }> }
) {
  const params = await props.params;
  return handleRequest(request, params.path);
}

export async function POST(
  request: NextRequest,
  props: { params: Promise<{ path: string[] }> }
) {
  const params = await props.params;
  return handleRequest(request, params.path);
}

export async function PUT(
  request: NextRequest,
  props: { params: Promise<{ path: string[] }> }
) {
  const params = await props.params;
  return handleRequest(request, params.path);
}

export async function PATCH(
  request: NextRequest,
  props: { params: Promise<{ path: string[] }> }
) {
  const params = await props.params;
  return handleRequest(request, params.path);
}

export async function DELETE(
  request: NextRequest,
  props: { params: Promise<{ path: string[] }> }
) {
  const params = await props.params;
  return handleRequest(request, params.path);
}

export async function HEAD(
  request: NextRequest,
  props: { params: Promise<{ path: string[] }> }
) {
  const params = await props.params;
  return handleRequest(request, params.path);
}

export async function OPTIONS(
  request: NextRequest,
  props: { params: Promise<{ path: string[] }> }
) {
  const params = await props.params;
  return handleRequest(request, params.path);
}

const MOCK_PERSONA = {
  id: 0,
  name: "CertiBot",
  description: "Assistant Qualiopi pour les organismes de formation",
  tools: [],
  starter_messages: [
    {
      name: "Audit Qualiopi",
      description: "Lancer un audit de conformite Qualiopi",
      message: "Je souhaite verifier la conformite de mon dossier Qualiopi.",
    },
  ],
  document_sets: [],
  is_public: true,
  is_visible: true,
  display_priority: 0,
  is_default_persona: true,
  builtin_persona: false,
  labels: [],
  owner: null,
};

const MOCK_LLM_PROVIDER = {
  name: "mock-provider",
  provider: "openai",
  provider_display_name: "OpenAI",
  default_model_name: "gpt-4o",
  is_default_provider: true,
  is_default_vision_provider: true,
  default_vision_model: "gpt-4o",
  is_public: true,
  groups: [],
  personas: [],
  model_configurations: [
    {
      model_name: "gpt-4o",
      model_display_name: "GPT-4o",
    },
  ],
};

function getMockResponse(pathStr: string): unknown | null {
  if (pathStr === "chat/get-user-chat-sessions") {
    return { sessions: [] };
  }
  if (pathStr === "persona") {
    return [MOCK_PERSONA];
  }
  if (pathStr === "manage/connector-status") {
    return [];
  }
  if (pathStr === "query/valid-tags") {
    return { tags: [] };
  }
  if (pathStr === "manage/document-set") {
    return [];
  }
  if (pathStr === "federated") {
    return [];
  }
  if (pathStr === "llm/provider") {
    return [MOCK_LLM_PROVIDER];
  }
  if (pathStr.match(/^llm\/persona\/\d+\/providers$/)) {
    return [MOCK_LLM_PROVIDER];
  }
  if (pathStr === "user/projects/" || pathStr === "user/projects") {
    return [];
  }
  if (pathStr === "user/files/recent") {
    return [];
  }
  if (pathStr === "notifications") {
    return [];
  }
  if (pathStr === "me") {
    return {
      id: "mock-user-dev",
      email: "dev@certibot.com",
      is_active: true,
      is_superuser: true,
      is_verified: true,
      role: "admin",
      preferences: { chosen_assistants: null, auto_scroll: true },
    };
  }
  if (pathStr === "settings") {
    return {
      auto_scroll: true,
      application_status: "active",
      gpu_enabled: false,
      maximum_chat_retention_days: null,
      notifications: [],
      needs_reindexing: false,
      anonymous_user_enabled: true,
      deep_research_enabled: true,
      temperature_override_enabled: true,
      query_history_type: "normal",
    };
  }
  if (pathStr === "health") {
    return { status: "ok" };
  }
  if (pathStr.match(/^user\/projects\/.*\/token-count$/)) {
    return { total_tokens: 0 };
  }
  if (pathStr.match(/^user\/projects\/session\/.*\/token-count$/)) {
    return { total_tokens: 0 };
  }
  if (pathStr.match(/^user\/projects\/session\/.*\/files$/)) {
    return [];
  }
  if (pathStr === "query-history/config") {
    return { query_history_type: "normal" };
  }
  if (pathStr.match(/^persona\/\d+$/)) {
    return MOCK_PERSONA;
  }
  return null;
}

async function handleRequest(request: NextRequest, path: string[]) {
  if (
    process.env.NODE_ENV !== "development" &&
    // NOTE: Set this environment variable to 'true' for preview environments
    // Where you want finer-grained control over API access
    process.env.OVERRIDE_API_PRODUCTION !== "true"
  ) {
    return NextResponse.json(
      {
        message:
          "This API is only available in development mode. In production, something else (e.g. nginx) should handle this.",
      },
      { status: 404 }
    );
  }

  try {
    const backendUrl = new URL(`${INTERNAL_URL}/${path.join("/")}`);

    // Get the URL parameters from the request
    const urlParams = new URLSearchParams(request.url.split("?")[1]);

    // Append the URL parameters to the backend URL
    urlParams.forEach((value, key) => {
      backendUrl.searchParams.append(key, value);
    });

    // Build headers, optionally injecting debug auth cookie
    const headers = new Headers(request.headers);
    if (
      process.env.DEBUG_AUTH_COOKIE &&
      process.env.NODE_ENV === "development"
    ) {
      // Inject the debug auth cookie for local development against remote backend
      // Get from cloud site: DevTools → Application → Cookies → fastapiusersauth
      const existingCookies = headers.get("cookie") || "";
      const debugCookie = `fastapiusersauth=${process.env.DEBUG_AUTH_COOKIE}`;
      headers.set(
        "cookie",
        existingCookies ? `${existingCookies}; ${debugCookie}` : debugCookie
      );
    }

    const response = await fetch(backendUrl, {
      method: request.method,
      headers: headers,
      body: request.body,
      signal: request.signal,
      // @ts-ignore
      duplex: "half",
    });

    // Check if the response is a stream
    if (
      response.headers.get("Transfer-Encoding") === "chunked" ||
      response.headers.get("Content-Type")?.includes("stream")
    ) {
      // If it's a stream, create a TransformStream to pass the data through
      const { readable, writable } = new TransformStream();
      response.body?.pipeTo(writable);

      return new NextResponse(readable, {
        status: response.status,
        headers: response.headers,
      });
    } else {
      return new NextResponse(response.body, {
        status: response.status,
        headers: response.headers,
      });
    }
  } catch (error: unknown) {
    const pathStr = path.join("/");
    const mockData = getMockResponse(pathStr);

    if (mockData !== null) {
      return NextResponse.json(mockData);
    }

    console.error("Proxy error (no mock available):", pathStr, error);
    return NextResponse.json(
      {
        message: "Proxy error",
        error:
          error instanceof Error ? error.message : "An unknown error occurred",
      },
      { status: 500 }
    );
  }
}
