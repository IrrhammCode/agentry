/**
 * Agentry Live API Client
 * Connects frontend directly to the running Agentry Python Sentry backend daemon.
 */

const API_BASE = 'http://127.0.0.1:8000';

export interface FleetMetrics {
  total_audited_steps: number;
  unique_sessions: number;
  interventions: {
    KILL: number;
    REROUTE: number;
    PAUSE: number;
    PASS: number;
  };
  total_tokens_saved: number;
  total_cost_saved_usd: number;
}

export interface AuditEvent {
  id: number;
  session_id: string;
  step_index: number;
  timestamp: number;
  action: 'PASS' | 'KILL' | 'PAUSE' | 'REROUTE';
  risk_level: 'NOMINAL' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  failure_probability: number;
  predicted_failure_mode: string;
  projected_final_cost_usd: number;
  confidence: number;
  reason: string;
  reroute_instruction: string | null;
  estimated_tokens_saved: number;
  estimated_cost_saved_usd: number;
  sentry_provider: string;
}

export interface AuditResult {
  session_id: string;
  step_index: number;
  action: 'PASS' | 'KILL' | 'PAUSE' | 'REROUTE';
  risk_level: string;
  confidence: number;
  failure_probability: number;
  predicted_failure_mode: string;
  projected_final_cost_usd: number;
  reason: string;
  reroute_instruction?: string;
  estimated_tokens_saved: number;
  estimated_cost_saved_usd: number;
  sentry_provider: string;
  latency_ms?: number;
}

export interface HITLApproval {
  request_id: string;
  session_id: string;
  step_index: number;
  tool_name: string;
  action: string;
  risk_level: string;
  failure_probability: number;
  predicted_failure_mode: string;
  reason: string;
  created_at: number;
  status: 'PENDING' | 'APPROVED_RESUME' | 'REROUTED' | 'REJECTED_ABORT' | 'TIMED_OUT';
  operator_comment?: string;
  custom_directive?: string;
  resolved_at?: number;
}

export interface DlpResult {
  original_text: string;
  masked_text: string;
  redaction_count: number;
  detected_secrets: Array<{ type: string; pattern?: string }>;
}

export interface BlastRadiusResult {
  score: number;
  score_raw: number;
  category: string;
  is_blocked: boolean;
  recommended_action: string;
  violation_reason?: string;
  matched_pattern?: string;
}

export interface SwarmDeadlockResult {
  is_deadlocked: boolean;
  cycle_agents: string[];
  cycle_length: number;
  recommendation: string;
}

export interface SourceMetrics {
  total_steps: number;
  unique_sessions: number;
  tokens_saved: number;
  cost_saved_usd: number;
  interventions: {
    KILL: number;
    REROUTE: number;
    PAUSE: number;
    PASS: number;
  };
}

export interface McpUsageResponse {
  sources: Record<string, SourceMetrics>;
  recent_mcp_events: AuditEvent[];
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error [${res.status}]: ${errorText}`);
  }
  return res.json() as Promise<T>;
}

export const AgentryApi = {
  // 1. Health check
  async getHealth() {
    return request<{
      status: string;
      service: string;
      version: string;
      tabpfn_engine_fitted: boolean;
      tabpfn_cloud_mode: boolean;
      local_slm_alive: boolean;
      local_slm_model: string;
    }>('/health');
  },

  // 2. Fleet Summary Metrics
  async getFleetMetrics(): Promise<FleetMetrics> {
    return request<FleetMetrics>('/v1/fleet');
  },

  // 3. Real Recorded Events
  async getAuditEvents(limit = 20): Promise<{ total: number; events: AuditEvent[] }> {
    return request<{ total: number; events: AuditEvent[] }>(`/v1/events?limit=${limit}`);
  },

  // 4. Live TabPFN Audit
  async auditStep(params: {
    session_id?: string;
    tool_name: string;
    input_text: string;
    output_text?: string;
    thought_trace?: string;
    agent_role?: string;
    model_name?: string;
    latency_ms?: number;
  }): Promise<AuditResult> {
    const t0 = performance.now();
    const result = await request<AuditResult>('/v1/audit', {
      method: 'POST',
      body: JSON.stringify(params),
    });
    const roundtrip = Math.round((performance.now() - t0) * 10) / 10;
    return { ...result, latency_ms: roundtrip };
  },

  // 5. HITL Approvals Queue
  async getApprovals(status?: string): Promise<{ total: number; requests: HITLApproval[] }> {
    const query = status ? `?status=${encodeURIComponent(status)}` : '';
    return request<{ total: number; requests: HITLApproval[] }>(`/v1/approvals${query}`);
  },

  // 6. Resolve HITL Request
  async resolveApproval(
    requestId: string,
    action: 'RESUME' | 'REROUTE' | 'ABORT',
    options?: { comment?: string; custom_directive?: string }
  ): Promise<{ status: string; request: HITLApproval }> {
    return request<{ status: string; request: HITLApproval }>(`/v1/approvals/${requestId}`, {
      method: 'POST',
      body: JSON.stringify({
        action,
        comment: options?.comment,
        custom_directive: options?.custom_directive,
      }),
    });
  },

  // 7. DLP Redact
  async redactDlp(text: string): Promise<DlpResult> {
    return request<DlpResult>('/v1/dlp/redact', {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
  },

  // 8. Blast Radius Evaluation
  async evaluateBlastRadius(toolName: string, command: string): Promise<BlastRadiusResult> {
    return request<BlastRadiusResult>('/v1/blast-radius/evaluate', {
      method: 'POST',
      body: JSON.stringify({ tool_name: toolName, command }),
    });
  },

  // 9. Swarm Deadlock Detection
  async detectDeadlock(
    sessionId: string,
    transfers: Array<{ from_agent: string; to_agent: string; task?: string }>
  ): Promise<SwarmDeadlockResult> {
    return request<SwarmDeadlockResult>('/v1/swarm/deadlock', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, transfers }),
    });
  },

  // 10. Global Emergency Suspend
  async emergencySuspend(): Promise<{ status: string; halted_sessions: number; message: string }> {
    return request<{ status: string; halted_sessions: number; message: string }>(
      '/v1/fleet/emergency-suspend',
      { method: 'POST', body: JSON.stringify({}) }
    );
  },

  // 11. MCP Usage Breakdown
  async getMcpUsage(): Promise<McpUsageResponse> {
    return request<McpUsageResponse>('/v1/mcp/usage');
  },

  // 12. Events by Source (mcp, rest, proxy, frontend)
  async getEventsBySource(source: string, limit = 20): Promise<{ source: string; total: number; events: AuditEvent[] }> {
    return request<{ source: string; total: number; events: AuditEvent[] }>(`/v1/events/${source}?limit=${limit}`);
  },
};
