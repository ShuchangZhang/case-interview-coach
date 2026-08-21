#!/usr/bin/env python3
"""Executable policy model for visible session boundaries and report triggers.

The live skill maintains this state conversationally.  This small standard-library
model makes the non-negotiable transitions testable: a drill pauses after every
rep, a presented-but-unanswered rep is not started, and every terminal path asks
for a report instead of silently opening another case.
"""


REP_STATUSES = ("not_presented", "presented", "started", "completed", "aborted")
DRILL_END_REASONS = (
    "completed_as_planned",
    "ended_early_between_reps",
    "aborted_mid_rep",
)


def _positive_int(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("{} must be a positive integer".format(name))


def new_focused_drill(planned_reps=3):
    """Return a newly announced drill with rep 1 presented but not started."""
    _positive_int(planned_reps, "planned_reps")
    return {
        "session_kind": "focused_drill",
        "planned_reps": planned_reps,
        "current_rep": 1,
        "completed_reps": 0,
        "rep_statuses": ["presented"] + ["not_presented"] * (planned_reps - 1),
        "awaiting_choice": False,
        "session_complete": False,
        "report_required": False,
        "completion": None,
        "session_end_reason": None,
    }


def _copy_open_drill(state):
    if state.get("session_kind") != "focused_drill":
        raise ValueError("state must describe a focused_drill")
    if state.get("session_complete"):
        raise ValueError("session is already complete")
    result = dict(state)
    result["rep_statuses"] = list(state.get("rep_statuses") or ())
    if len(result["rep_statuses"]) != result.get("planned_reps"):
        raise ValueError("rep_statuses must contain one entry per planned rep")
    return result


def start_current_rep(state):
    """A rep starts only after a substantive Candidate response."""
    result = _copy_open_drill(state)
    index = result["current_rep"] - 1
    if result["rep_statuses"][index] != "presented":
        raise ValueError("only a presented rep can be started")
    result["rep_statuses"][index] = "started"
    return result


def complete_current_rep(state):
    """Complete a rep, then pause or finish; never present the next rep here."""
    result = _copy_open_drill(state)
    index = result["current_rep"] - 1
    if result["rep_statuses"][index] != "started":
        raise ValueError("only a started rep can be completed")
    result["rep_statuses"][index] = "completed"
    result["completed_reps"] += 1

    if result["completed_reps"] == result["planned_reps"]:
        result.update({
            "awaiting_choice": False,
            "session_complete": True,
            "report_required": True,
            "completion": "complete",
            "session_end_reason": "completed_as_planned",
        })
    else:
        result["awaiting_choice"] = True
    return result


def continue_drill(state):
    """Present the next rep only after the user explicitly chooses Continue."""
    result = _copy_open_drill(state)
    if not result.get("awaiting_choice"):
        raise ValueError("continue is available only between completed reps")
    next_index = result["current_rep"]
    if next_index >= result["planned_reps"]:
        raise ValueError("there is no next rep")
    result["current_rep"] += 1
    result["rep_statuses"][next_index] = "presented"
    result["awaiting_choice"] = False
    return result


def end_between_reps(state):
    """End normally after a completed rep, including if the next was only shown."""
    result = _copy_open_drill(state)
    current_index = result["current_rep"] - 1
    current_status = result["rep_statuses"][current_index]
    valid_boundary = result.get("awaiting_choice") or (
        current_status == "presented" and result["completed_reps"] >= 1)
    if not valid_boundary:
        raise ValueError("normal early end is available only between reps")
    result.update({
        "awaiting_choice": False,
        "session_complete": True,
        "report_required": True,
        "completion": "complete",
        "session_end_reason": "ended_early_between_reps",
    })
    return result


def abort_mid_rep(state):
    """Stop an active rep and request an incomplete report."""
    result = _copy_open_drill(state)
    index = result["current_rep"] - 1
    if result["rep_statuses"][index] != "started":
        raise ValueError("mid-rep abort requires a started rep")
    result["rep_statuses"][index] = "aborted"
    result.update({
        "awaiting_choice": False,
        "session_complete": True,
        "report_required": True,
        "completion": "aborted",
        "session_end_reason": "aborted_mid_rep",
    })
    return result


def evaluated_reps(state):
    """Return 1-based reps with observable work; presented-only is excluded."""
    return tuple(i + 1 for i, status in enumerate(state.get("rep_statuses") or ())
                 if status in ("completed", "aborted"))


def boundary_message(state, language="en"):
    """Make the mandatory between-rep progress and choice visible."""
    if not state.get("awaiting_choice"):
        return ""
    completed = state["completed_reps"]
    planned = state["planned_reps"]
    if language == "zh":
        return ("第 {} / {} 题完成。继续第 {} 题，还是现在结束专项练习并生成报告？"
                .format(completed, planned, completed + 1))
    return ("Rep {} / {} complete. Continue to rep {}, or end the focused drill "
            "now and generate the report?".format(completed, planned, completed + 1))


def full_case_completed():
    """A completed full case terminates at review; it never auto-starts another."""
    return {
        "session_kind": "full_case",
        "session_complete": True,
        "report_required": True,
        "completion": "complete",
        "auto_start_next_case": False,
    }
