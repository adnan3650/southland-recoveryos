"""Deterministic documentation checks. Never a safety or eligibility decision."""


def readiness(case):
    docs = case["documents"]
    categories = {doc["category"] for doc in docs}
    checks = [
        (
            "photos",
            "Damage photographs",
            any(d["media_type"].startswith("image/") and d["category"] == "damage" for d in docs),
            "Upload photographs taken only where safe.",
        ),
        (
            "inventory",
            "Damage inventory",
            bool(case["damage_items"]),
            "Record affected belongings and areas; mark uncertainty.",
        ),
        ("policy", "Insurance policy", "policy" in categories, "Add the policy or ask your insurer for a copy."),
        (
            "claim",
            "Insurer contact record",
            bool(case["insurance"].get("insurer"))
            and any(
                contact["organization"].strip().casefold() == case["insurance"]["insurer"].strip().casefold()
                for contact in case["contacts"]
            ),
            "Save your insurer and a dated contact note using the same organization name.",
        ),
        (
            "receipts",
            "Receipts and estimates",
            bool(categories & {"receipt", "estimate"}),
            "Keep receipts and written repair estimates.",
        ),
    ]
    items = [{"id": k, "title": t, "complete": bool(ok), "next_step": hint} for k, t, ok, hint in checks]
    return {
        "percent": round(sum(c["complete"] for c in items) / len(items) * 100),
        "checks": items,
        "meaning": "Documentation completeness only. This is not a measure of safety, coverage or eligibility.",
    }


def initial_tasks(case):
    tasks = [
        (
            "safety",
            "Confirm your immediate safety",
            "For an immediate threat call 911. Avoid flooded areas and damaged structures; follow official responders.",
            "urgent",
            "flood-safety",
        ),
        (
            "evidence",
            "Document damage where it is safe",
            "Add photos and a list of affected belongings. Do not enter an unsafe area to collect evidence.",
            "high",
            "county-floods",
        ),
        (
            "insurance",
            "Contact your insurer",
            "Ask how to report the loss, what deadlines apply, and what evidence they need. Coverage requires insurer review.",
            "high",
            "county-floods",
        ),
        (
            "receipts",
            "Keep receipts and written estimates",
            "Organize lodging, replacement and repair expenses. Ask about requirements before starting work.",
            "normal",
            "county-floods",
        ),
        (
            "assistance",
            "Confirm assistance requirements",
            "Review local referrals and confirm program availability with the responsible agency.",
            "normal",
            "211",
        ),
    ]
    if case["displaced"] or case["immediate_needs"]:
        tasks.insert(
            1,
            (
                "essentials",
                "Arrange shelter and essential needs",
                "Contact 211 for local referrals; confirm hours and availability directly before traveling.",
                "urgent",
                "211",
            ),
        )
    return [
        {
            "id": key,
            "title": title,
            "explanation": desc,
            "priority": priority,
            "source_id": source,
            "status": "todo",
            "due_date": None,
            "required_information": [],
            "responsible_party": "Resident with agency support",
            "provenance": "deterministic guidance",
        }
        for key, title, desc, priority, source in tasks
    ]


def match_programs(case, resources):
    categories = {d["category"] for d in case["documents"]}
    result = []
    for resource in resources:
        if not resource.get("program"):
            continue
        status = "More information required"
        reasons, missing = [], []
        if resource["id"] == "south-holland-flood":
            if (
                case["municipality"].casefold() != "south holland"
                or case["disaster_type"] not in ["flood", "storm"]
                or case["property_situation"] == "renter"
            ):
                status = "Published requirements appear not to match"
                reasons.append(
                    "Published mitigation guidance is for qualifying South Holland homeowner flood-prevention projects."
                )
            else:
                status = "Potentially relevant" if case["property_situation"] == "owner" else status
                missing.extend(
                    [
                        "Village pre-approval before work",
                        "Confirm owner occupancy",
                        "Confirm qualifying mitigation project and current funding",
                        "Two contractor bids",
                    ]
                )
                if "estimate" not in categories:
                    missing.append("Contractor estimates")
                reasons.append(
                    "A prevention rebate is not an automatic reimbursement for storm damage. Village review required."
                )
        elif resource["id"] == "fema":
            status = "Current availability unverified"
            missing.extend(
                [
                    "Confirm disaster declaration covers this incident date and location",
                    "Confirm application window and household requirements",
                    "Identity and occupancy documentation",
                    "Insurance settlement or denial information if applicable",
                ]
            )
            reasons.append(
                "No federal declaration has been verified for the saved incident. Never infer approval from a state proclamation."
            )
        elif resource["id"] == "county-recovery":
            status = "Current availability unverified"
            reasons.append(
                "Published recovery planning is tied to specified prior disasters. It does not establish coverage of this case."
            )
            missing.extend(
                [
                    "Confirm covered incident and geographic area",
                    "Confirm open applications and published household requirements",
                ]
            )
        result.append(
            {
                **resource,
                "match_status": status,
                "reasons": reasons,
                "missing_requirements": missing,
                "final_eligibility": False,
            }
        )
    return result


def prioritized_plan(case, resources):
    order = {"urgent": 0, "high": 1, "normal": 2}
    return sorted(case["tasks"], key=lambda t: (t["status"] == "done", order[t["priority"]]))
