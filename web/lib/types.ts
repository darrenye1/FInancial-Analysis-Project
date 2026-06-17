export interface AnalysisData {
  ticker: string;
  company: {
    name: string;
    sector: string;
    industry: string;
    employees: number;
    marketCap: number;
    currency: string;
  };
  highlights: {
    latestYear: number;
    revenue: number;
    netIncome: number;
    netMargin: number | null;
    grossMargin: number | null;
    revenueYoY: number | null;
    freeCashFlow: number | null;
    roe: number | null;
    cashConversionCycle: number | null;
  };
  pl: {
    incomeStatement: Record<string, number | string | null>[];
    margins: Record<string, number | string | null>[];
    growth: Record<string, number | string | null>[];
    expenseBreakdown: Record<string, number | string | null>[];
  };
  budget: {
    summary: Record<string, number | string | null>[];
    variance: Record<string, number | string | null>[];
  };
  forecast: {
    revenue: Record<string, number | string | null>[];
    multiMetric: Record<string, number | string | null>[];
    scenarios: { Year: number; Scenario: string; "Total Revenue": number }[];
  };
  sensitivity: {
    oneWay: Record<string, number | null>[];
    twoWay: { columns: string[]; rows: Record<string, number | string | null>[] };
    tornado: { Driver: string; "Low Case": number; "High Case": number; Base: number; Range: number }[];
  };
  corpFin: {
    cashFlow: Record<string, number | string | null>[];
    workingCapital: Record<string, number | string | null>[];
    dupont: Record<string, number | string | null>[];
    capitalStructure: Record<string, number | string | null>[];
    marginBridge: Record<string, number | string | null>[];
  };
  stockPrice: { date: string; close: number; volume: number }[];
  generatedAt: string;
}
