import type { AnalysisData } from "./types";
import raw from "@/data/analysis.json";

export type { AnalysisData } from "./types";
export { formatBillions, formatPercent } from "./format";
export const analysisData = raw as AnalysisData;
