import json
from typing import Any

from app.schemas import RankingRule, ScreeningRule


FUNDAMENTAL_FIELDS = {
    "market_cap", "pe_ratio", "pb_ratio", "dividend_yield", "roe",
    "revenue", "profit_margin", "debt_to_equity", "eps", "beta", "roce", "pat"
}


class StrategyEngine:
    def apply_screening(
        self, candidates: list[dict[str, Any]], rules: list[ScreeningRule]
    ) -> list[dict[str, Any]]:
        if not rules:
            return candidates

        filtered = []
        for candidate in candidates:
            if self._passes_all_rules(candidate, rules):
                filtered.append(candidate)
        return filtered

    def rank_stocks(
        self, candidates: list[dict[str, Any]], rules: list[RankingRule]
    ) -> list[dict[str, Any]]:
        if not candidates:
            return []

        if not rules:
            return sorted(candidates, key=lambda c: c.get("symbol", ""))

        # We will compute ordinal ranks for each rule
        # rule_ranks: list of dicts mapping symbol -> rank (1 to M, where 1 is best)
        rule_ranks: list[dict[str, int]] = []

        for rule in rules:
            valid_candidates = []
            invalid_candidates = []

            for c in candidates:
                val = c.get(rule.field)
                if val is not None:
                    valid_candidates.append(c)
                else:
                    invalid_candidates.append(c)

            # Sort valid candidates:
            # If descending, larger value is better, so rank 1 is highest value
            # If ascending, smaller value is better, so rank 1 is lowest value
            reverse_sort = (rule.direction == "desc")
            try:
                sorted_valid = sorted(
                    valid_candidates,
                    key=lambda x: float(x.get(rule.field) if x.get(rule.field) is not None else 0),
                    reverse=reverse_sort
                )
            except (TypeError, ValueError):
                # Fallback in case of conversion errors
                sorted_valid = sorted(
                    valid_candidates,
                    key=lambda x: str(x.get(rule.field)),
                    reverse=reverse_sort
                )

            # Assign ranks (1-indexed)
            ranks = {}
            for i, c in enumerate(sorted_valid):
                ranks[c["symbol"]] = i + 1

            # For invalid candidates, assign a default bad rank (M + 1)
            bad_rank = len(candidates) + 1
            for c in invalid_candidates:
                ranks[c["symbol"]] = bad_rank

            rule_ranks.append(ranks)

        # Now compute the weighted average rank score for each candidate
        total_weight = sum(rule.weight for rule in rules) or 1.0
        scored = []
        for c in candidates:
            weighted_rank_sum = 0.0
            for idx, rule in enumerate(rules):
                rank = rule_ranks[idx].get(c["symbol"], len(candidates) + 1)
                weighted_rank_sum += rank * rule.weight

            avg_rank_score = weighted_rank_sum / total_weight

            enriched = dict(c)
            enriched["score"] = avg_rank_score  # lower rank score is better!
            scored.append(enriched)

        # Sort candidates by score ascending (lowest rank score is best)
        # So the top N stocks will be the ones with the lowest score
        return sorted(scored, key=lambda c: c["score"])

    def select_top_n(
        self,
        candidates: list[dict[str, Any]],
        screening_rules: list[ScreeningRule],
        ranking_rules: list[RankingRule],
        top_n: int,
    ) -> list[dict[str, Any]]:
        screened = self.apply_screening(candidates, screening_rules)
        ranked = self.rank_stocks(screened, ranking_rules)
        return ranked[:top_n]

    def _passes_all_rules(self, candidate: dict[str, Any], rules: list[ScreeningRule]) -> bool:
        for rule in rules:
            value = candidate.get(rule.field)
            if value is None:
                return False
            try:
                if not self._evaluate_rule(float(value), rule):
                    return False
            except (TypeError, ValueError):
                return False
        return True

    def _evaluate_rule(self, value: float, rule: ScreeningRule) -> bool:
        if rule.operator == "gt":
            return value > float(rule.value)
        if rule.operator == "gte":
            return value >= float(rule.value)
        if rule.operator == "lt":
            return value < float(rule.value)
        if rule.operator == "lte":
            return value <= float(rule.value)
        if rule.operator == "eq":
            return value == float(rule.value)
        if rule.operator == "between":
            low, high = rule.value if isinstance(rule.value, list) else [rule.value, rule.value]
            return float(low) <= value <= float(high)
        return False


def parse_strategy_rules(screening_json: str, ranking_json: str) -> tuple[list[ScreeningRule], list[RankingRule]]:
    screening_data = json.loads(screening_json or "[]")
    ranking_data = json.loads(ranking_json or "[]")
    screening = [ScreeningRule.model_validate(r) for r in screening_data]
    ranking = [RankingRule.model_validate(r) for r in ranking_data]
    return screening, ranking
