export interface FeatureContributor {
  feature: string;
  attribution: number;
  feature_value: number;
}

export interface ScoreResult {
  transaction_id: string;
  risk_score: number;
  risk_band: string;
  model_version: string;
  top_contributors: FeatureContributor[];
  alerted: boolean;
  enriched?: boolean;
  user_known?: boolean;
}

export interface Alert {
  transaction_id: string;
  user_id: string;
  risk_score: number;
  risk_band: string;
  top_contributors: FeatureContributor[];
  narration: string;
  created_at: string;
}

export interface AlertsResponse {
  alerts: Alert[];
  total_alerts: number;
  limit: number;
}

export type HealthStatus = Record<string, string>;
