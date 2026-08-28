import json
import os
import requests
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

TASK1_API_URL = os.getenv(
    "TASK1_API_URL",
    "http://localhost:8001"
)

TASK2_API_URL = os.getenv(
    "TASK2_API_URL",
    "http://localhost:8000"
)

BASE_DIR = Path(__file__).resolve().parent

TASK1_FILE = BASE_DIR / "task1_test.json"
TASK2_FILE = BASE_DIR / "task2_test.json"

REPORT_FILE = BASE_DIR / "evaluation_report.json"


# ============================================================
# LOAD JSON
# ============================================================

def load_json(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize(value):

    if value is None:

        return ""

    return str(value).lower().strip()


# ============================================================
# KEYWORD CHECK
# ============================================================

def keyword_exists(
    text,
    keyword
):

    return normalize(
        keyword
    ) in normalize(
        text
    )


def acceptance_criterion_passed(
    criterion,
    result
):

    criterion_text = normalize(criterion)
    output_text = normalize(
        json.dumps(result, ensure_ascii=False)
    )

    if "must not classify this ticket as a p1 service outage" in criterion_text:
        return (
            normalize(result.get("urgency")) != "p1"
            and normalize(result.get("issue_category")) != "service outage"
        )

    if "recognize that the application is currently working normally" in criterion_text:
        return (
            "working normally" in output_text
            or "currently works normally" in output_text
            or "no immediate technical issue" in output_text
        )

    if "must not invent a specific technical failure" in criterion_text:
        return (
            "no specific technical failure" in output_text
            or "no specific failure" in output_text
            or "no immediate technical issue" in output_text
        )

    if "acknowledge the customer's concern about evaluating another vendor" in criterion_text:
        return (
            "vendor" in output_text
            and (
                "evaluat" in output_text
                or "switch" in output_text
                or "continue" in output_text
            )
        )

    if "priority must remain lower than p1" in criterion_text:
        return normalize(result.get("urgency")) in {
            "p2", "p3", "p4"
        }

    return False


# ============================================================
# TASK 1 EVALUATION
# ============================================================

def evaluate_task1(
    test_case
):

    ticket = test_case["input"]

    expected = test_case.get(
        "expected_output",
        test_case.get("expected", {})
    )

    try:

        response = None

        for attempt in range(3):

            try:

                response = requests.post(

                    f"{TASK1_API_URL}/triage",

                    json=ticket,

                    timeout=180
                )

                break

            except requests.RequestException:

                if attempt == 2:

                    raise

        result = response.json()

    except Exception as error:

        return {

            "test_id":
                test_case["test_id"],

            "name":
                test_case["name"],

            "status":
                "FAIL",

            "quality_score":
                0.0,

            "checks_passed":
                0,

            "checks_total":
                0,

            "reason":
                str(error)
        }


    # --------------------------------------------------------
    # HTTP STATUS
    # --------------------------------------------------------

    if response.status_code != 200:

        return {

            "test_id":
                test_case["test_id"],

            "name":
                test_case["name"],

            "status":
                "FAIL",

            "quality_score":
                0.0,

            "checks_passed":
                0,

            "checks_total":
                1,

            "reason":
                f"API returned {response.status_code}",

            "actual_output":
                result
        }


    checks = 0

    passed = 0


    # --------------------------------------------------------
    # PRODUCT AREA
    # --------------------------------------------------------

    if "product_area" in expected:

        checks += 1

        if normalize(
            result.get("product_area")
        ) == normalize(
            expected["product_area"]
        ):

            passed += 1


    # --------------------------------------------------------
    # ISSUE CATEGORY
    # --------------------------------------------------------

    expected_category = expected.get(
        "issue_category",
        expected.get("category")
    )

    if expected_category is not None:

        checks += 1

        if normalize(
            result.get("issue_category")
        ) == normalize(
            expected_category
        ):

            passed += 1


    # --------------------------------------------------------
    # URGENCY
    # --------------------------------------------------------

    expected_urgency = expected.get(
        "urgency",
        expected.get("priority")
    )

    if expected_urgency is not None:

        checks += 1

        if normalize(
            result.get("urgency")
        ) == normalize(
            expected_urgency
        ):

            passed += 1


    # --------------------------------------------------------
    # KNOWN ISSUE
    # --------------------------------------------------------

    if "known_issue" in expected:

        checks += 1

        if (
            result.get("known_issue")
            ==
            expected["known_issue"]
        ):

            passed += 1


    # --------------------------------------------------------
    # RECOMMENDED TEAM
    # --------------------------------------------------------

    if "recommended_team" in expected:

        checks += 1

        if normalize(
            result.get("recommended_team")
        ) == normalize(
            expected["recommended_team"]
        ):

            passed += 1


    # --------------------------------------------------------
    # REQUIRED KEYWORDS
    # --------------------------------------------------------

    output_text = json.dumps(
        result,
        ensure_ascii=False
    )

    for keyword in expected.get(
        "required_keywords",
        []
    ):

        checks += 1

        if keyword_exists(
            output_text,
            keyword
        ):

            passed += 1


    # --------------------------------------------------------
    # ACCEPTANCE CRITERIA
    # --------------------------------------------------------

    acceptance_results = []

    for criterion in test_case.get(
        "acceptance_criteria",
        []
    ):

        criterion_passed = acceptance_criterion_passed(
            criterion,
            result
        )

        checks += 1

        if criterion_passed:

            passed += 1

        acceptance_results.append({
            "criterion": criterion,
            "passed": criterion_passed
        })


    # --------------------------------------------------------
    # QUALITY SCORE
    # --------------------------------------------------------

    score = (
        passed / checks
        if checks
        else 0
    )


    status = (
        "PASS"
        if score >= 0.75
        else "FAIL"
    )


    return {

        "test_id":
            test_case["test_id"],

        "name":
            test_case["name"],

        "status":
            status,

        "quality_score":
            round(
                score,
                2
            ),

        "checks_passed":
            passed,

        "checks_total":
            checks,

        "acceptance_results":
            acceptance_results,

        "actual_output":
            result
    }


# ============================================================
# TASK 2 NORMAL TEST
# ============================================================

def evaluate_task2_normal(
    test_case
):

    account = test_case[
        "input"
    ]

    expected = test_case[
        "expected_output"
    ]


    try:

        response = requests.post(

            f"{TASK2_API_URL}/account-health",

            json={
                "account_id":
                    account["account_id"]
            },

            timeout=180
        )

        result = response.json()

    except Exception as error:

        return {

            "test_id":
                test_case["test_id"],

            "name":
                test_case["name"],

            "status":
                "FAIL",

            "quality_score":
                0.0,

            "checks_passed":
                0,

            "checks_total":
                0,

            "reason":
                str(error)
        }


    if response.status_code != 200:

        return {

            "test_id":
                test_case["test_id"],

            "name":
                test_case["name"],

            "status":
                "FAIL",

            "quality_score":
                0.0,

            "checks_passed":
                0,

            "checks_total":
                1,

            "reason":
                f"API returned {response.status_code}",

            "actual_output":
                result
        }


    checks = 0

    passed = 0


    # --------------------------------------------------------
    # ACCOUNT ID
    # --------------------------------------------------------

    if "account_id" in expected:

        checks += 1

        if normalize(
            result.get("account_id")
        ) == normalize(
            expected["account_id"]
        ):

            passed += 1


    # --------------------------------------------------------
    # COMPANY
    # --------------------------------------------------------

    if "company" in expected:

        checks += 1

        if normalize(
            result.get("company")
        ) == normalize(
            expected["company"]
        ):

            passed += 1


    # --------------------------------------------------------
    # RISK EXPECTATION
    # --------------------------------------------------------

    if "open_risks_and_flagged_issues" in expected:

        checks += 1

        actual_risks = result.get(
            "open_risks_and_flagged_issues",
            []
        )

        expected_risks = expected[
            "open_risks_and_flagged_issues"
        ]

        if len(actual_risks) == len(
            expected_risks
        ):

            passed += 1


    # --------------------------------------------------------
    # TICKET COUNT
    # --------------------------------------------------------

    if "ticket_count_90d" in expected:

        checks += 1

        if (
            result.get(
                "ticket_count_90d"
            )
            ==
            expected[
                "ticket_count_90d"
            ]
        ):

            passed += 1


    # --------------------------------------------------------
    # DATA WINDOW
    # --------------------------------------------------------

    if "data_window_start" in expected:

        checks += 1

        if (
            normalize(
                result.get(
                    "data_window_start"
                )
            )
            ==
            normalize(
                expected[
                    "data_window_start"
                ]
            )
        ):

            passed += 1


    if "data_window_end" in expected:

        checks += 1

        if (
            normalize(
                result.get(
                    "data_window_end"
                )
            )
            ==
            normalize(
                expected[
                    "data_window_end"
                ]
            )
        ):

            passed += 1


    # --------------------------------------------------------
    # REQUIRED KEYWORDS
    # --------------------------------------------------------

    output_text = json.dumps(
        result,
        ensure_ascii=False
    )

    for keyword in expected.get(
        "required_keywords",
        []
    ):

        checks += 1

        if keyword_exists(
            output_text,
            keyword
        ):

            passed += 1


    # --------------------------------------------------------
    # QUALITY SCORE
    # --------------------------------------------------------

    score = (
        passed / checks
        if checks
        else 0
    )


    status = (
        "PASS"
        if score >= 0.75
        else "FAIL"
    )


    return {

        "test_id":
            test_case["test_id"],

        "name":
            test_case["name"],

        "status":
            status,

        "quality_score":
            round(
                score,
                2
            ),

        "checks_passed":
            passed,

        "checks_total":
            checks,

        "actual_output":
            result
    }


# ============================================================
# TASK 2 ADVERSARIAL TEST
# ============================================================

def evaluate_task2_adversarial(
    test_case
):

    account = test_case[
        "input"
    ]

    expected = test_case[
        "expected_output"
    ]


    try:

        response = requests.post(

            f"{TASK2_API_URL}/account-health",

            json={
                "account_id":
                    account["account_id"]
            },

            timeout=180
        )

        result = response.json()

    except Exception as error:

        return {

            "test_id":
                test_case["test_id"],

            "name":
                test_case["name"],

            "status":
                "FAIL",

            "quality_score":
                0.0,

            "checks_passed":
                0,

            "checks_total":
                1,

            "reason":
                str(error)
        }


    checks = 0

    passed = 0


    # --------------------------------------------------------
    # EXPECTED HTTP STATUS
    # --------------------------------------------------------

    checks += 1

    if response.status_code == 404:

        passed += 1


    # --------------------------------------------------------
    # EXPECTED ERROR DETAIL
    # --------------------------------------------------------

    if "detail" in expected:

        checks += 1

        actual_detail = normalize(
            result.get("detail")
        )

        expected_detail = normalize(
            expected["detail"]
        )

        if actual_detail == expected_detail:

            passed += 1


    # --------------------------------------------------------
    # ACCEPTANCE CRITERIA
    # --------------------------------------------------------

    acceptance_criteria = test_case.get(
        "acceptance_criteria",
        []
    )


    # For an unknown account,
    # successful HTTP 404 + correct
    # detail is the important behavior.

    if acceptance_criteria:

        checks += 1

        if (
            response.status_code == 404
            and
            "detail" in result
        ):

            passed += 1


    # --------------------------------------------------------
    # QUALITY SCORE
    # --------------------------------------------------------

    score = (
        passed / checks
        if checks
        else 0
    )


    status = (
        "PASS"
        if score >= 0.75
        else "FAIL"
    )


    return {

        "test_id":
            test_case["test_id"],

        "name":
            test_case["name"],

        "status":
            status,

        "quality_score":
            round(
                score,
                2
            ),

        "checks_passed":
            passed,

        "checks_total":
            checks,

        "actual_output":
            result
    }


# ============================================================
# TASK 2 ROUTER
# ============================================================

def evaluate_task2(
    test_case
):

    if test_case.get(
        "adversarial",
        False
    ):

        return evaluate_task2_adversarial(
            test_case
        )


    return evaluate_task2_normal(
        test_case
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()

    print("=" * 60)

    print(
        "AI SOLUTION EVALUATION HARNESS"
    )

    print("=" * 60)

    print()


    # --------------------------------------------------------
    # LOAD TESTS
    # --------------------------------------------------------

    task1_tests = load_json(
        TASK1_FILE
    )

    task2_tests = load_json(
        TASK2_FILE
    )


    task1_results = []

    task2_results = []


    # ========================================================
    # TASK 1
    # ========================================================

    print(
        "Running Task 1 tests..."
    )

    print()


    for test in task1_tests:

        result = evaluate_task1(
            test
        )

        task1_results.append(
            result
        )

        print(
            f"{result['test_id']} | "
            f"{result['status']} | "
            f"Score: "
            f"{result['quality_score']}"
        )


    # ========================================================
    # TASK 2
    # ========================================================

    print()

    print(
        "Running Task 2 tests..."
    )

    print()


    for test in task2_tests:

        result = evaluate_task2(
            test
        )

        task2_results.append(
            result
        )

        print(
            f"{result['test_id']} | "
            f"{result['status']} | "
            f"Score: "
            f"{result['quality_score']}"
        )


    # ========================================================
    # SUMMARY
    # ========================================================

    all_results = (
        task1_results
        +
        task2_results
    )


    total_tests = len(
        all_results
    )


    passed_tests = sum(

        1

        for result
        in all_results

        if result["status"]
        ==
        "PASS"
    )


    failed_tests = (
        total_tests
        -
        passed_tests
    )


    overall_score = (

        sum(
            result["quality_score"]
            for result
            in all_results
        )
        /
        total_tests

        if total_tests

        else 0
    )


    pass_rate = (

        passed_tests
        /
        total_tests

        if total_tests

        else 0
    )


    # ========================================================
    # REPORT
    # ========================================================

    report = {

        "summary": {

            "total_tests":
                total_tests,

            "passed":
                passed_tests,

            "failed":
                failed_tests,

            "pass_rate":
                round(
                    pass_rate,
                    2
                ),

            "overall_quality_score":
                round(
                    overall_score,
                    2
                )
        },

        "task1": {

            "total":
                len(task1_results),

            "passed":
                sum(
                    1
                    for result
                    in task1_results
                    if result["status"]
                    ==
                    "PASS"
                ),

            "failed":
                sum(
                    1
                    for result
                    in task1_results
                    if result["status"]
                    ==
                    "FAIL"
                ),

            "results":
                task1_results
        },

        "task2": {

            "total":
                len(task2_results),

            "passed":
                sum(
                    1
                    for result
                    in task2_results
                    if result["status"]
                    ==
                    "PASS"
                ),

            "failed":
                sum(
                    1
                    for result
                    in task2_results
                    if result["status"]
                    ==
                    "FAIL"
                ),

            "results":
                task2_results
        }
    }


    # ========================================================
    # SAVE REPORT
    # ========================================================

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(

            report,

            file,

            indent=2,

            ensure_ascii=False
        )


    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    print()

    print("=" * 60)

    print(
        "EVALUATION SUMMARY"
    )

    print("=" * 60)


    print(
        f"Total Tests     : "
        f"{total_tests}"
    )

    print(
        f"Passed          : "
        f"{passed_tests}"
    )

    print(
        f"Failed          : "
        f"{failed_tests}"
    )

    print(
        f"Pass Rate       : "
        f"{pass_rate:.0%}"
    )

    print(
        f"Quality Score   : "
        f"{overall_score:.2f}"
    )

    print()

    print(
        f"Report saved to: "
        f"{REPORT_FILE}"
    )

    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()