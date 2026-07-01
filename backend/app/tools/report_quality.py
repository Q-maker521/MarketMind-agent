from typing import Any


REQUIRED_SECTION_TITLES = {"行情走势", "技术指标快照", "新闻与事件", "基准回测", "主要风险"}
DISCLAIMER_KEYWORDS = ("不构成", "投资建议")
UNSUPPORTED_PREDICTION_TERMS = ("必然", "一定", "稳赚", "保证收益", "无风险", "翻倍")
EVIDENCE_TOOL_NAMES = (
    "get_daily_prices",
    "calculate_basic_indicators",
    "run_buy_and_hold_backtest",
)


def evaluate_report_quality(report: dict[str, Any], tool_calls: list[dict[str, Any]]) -> dict[str, Any]:
    checks = [
        _check_required_sections(report),
        _check_disclaimer(report),
        _check_unsupported_predictions(report),
        _check_tool_evidence(tool_calls),
        _check_source_traceability(report),
    ]
    passed_count = sum(1 for check in checks if check["passed"])
    quality_score = round(passed_count / len(checks), 2)
    passed = all(check["passed"] for check in checks)

    return {
        "passed": passed,
        "quality_score": quality_score,
        "checks": checks,
        "summary": _build_review_summary(passed_count, len(checks), passed),
    }


def format_quality_summary(review_result: dict[str, Any]) -> str:
    status = "passed" if review_result["passed"] else "needs attention"
    return f"Report quality review {status}: score={review_result['quality_score']:.0%}, {review_result['summary']}"


def _check_required_sections(report: dict[str, Any]) -> dict[str, Any]:
    section_titles = {section.get("title", "") for section in report.get("sections", [])}
    missing_titles = sorted(REQUIRED_SECTION_TITLES - section_titles)
    return {
        "id": "required_sections",
        "label": "必需章节",
        "passed": not missing_titles,
        "severity": "high",
        "detail": "章节完整。" if not missing_titles else f"缺少章节：{', '.join(missing_titles)}。",
    }


def _check_disclaimer(report: dict[str, Any]) -> dict[str, Any]:
    disclaimer = report.get("disclaimer", "")
    passed = all(keyword in disclaimer for keyword in DISCLAIMER_KEYWORDS)
    return {
        "id": "disclaimer",
        "label": "免责声明",
        "passed": passed,
        "severity": "high",
        "detail": "已包含非投资建议声明。" if passed else "免责声明缺少关键表述。",
    }


def _check_unsupported_predictions(report: dict[str, Any]) -> dict[str, Any]:
    report_text = " ".join(
        [
            report.get("summary", ""),
            report.get("markdown", ""),
            " ".join(section.get("body", "") for section in report.get("sections", [])),
        ]
    )
    detected_terms = [term for term in UNSUPPORTED_PREDICTION_TERMS if term in report_text]
    return {
        "id": "unsupported_predictions",
        "label": "过度预测",
        "passed": not detected_terms,
        "severity": "medium",
        "detail": "未发现绝对化收益承诺。" if not detected_terms else f"发现敏感词：{', '.join(detected_terms)}。",
    }


def _check_tool_evidence(tool_calls: list[dict[str, Any]]) -> dict[str, Any]:
    successful_tool_names = [
        tool_call.get("tool_name", "")
        for tool_call in tool_calls
        if tool_call.get("status") == "SUCCESS"
    ]
    missing_tools = [
        expected_name
        for expected_name in EVIDENCE_TOOL_NAMES
        if not any(expected_name in tool_name for tool_name in successful_tool_names)
    ]
    return {
        "id": "tool_evidence",
        "label": "工具证据",
        "passed": not missing_tools,
        "severity": "high",
        "detail": "行情、指标和回测工具均有成功记录。" if not missing_tools else f"缺少工具证据：{', '.join(missing_tools)}。",
    }


def _check_source_traceability(report: dict[str, Any]) -> dict[str, Any]:
    sources = report.get("sources", [])
    source_types = {source.get("type") for source in sources}
    required_types = {"mock_data", "local_tool"}
    missing_types = sorted(required_types - source_types)
    return {
        "id": "source_traceability",
        "label": "来源追踪",
        "passed": not missing_types,
        "severity": "medium",
        "detail": "报告已附带数据和工具来源。" if not missing_types else f"缺少来源类型：{', '.join(missing_types)}。",
    }


def _build_review_summary(passed_count: int, total_count: int, passed: bool) -> str:
    if passed:
        return f"{passed_count}/{total_count} checks passed."
    return f"{passed_count}/{total_count} checks passed; manual review recommended."
