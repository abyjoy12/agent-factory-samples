#!/usr/bin/env python3
"""Prepare native Builder graphs for the AI World labs, without changing their wiring.

Generic cards size themselves in the product. Only sticky notes get explicit sizes.
Optional measured sizes come from the running editor, keyed by node ID.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB_MODEL = "AIW26-PAF-HOL6004-BOO6096"
COLUMN_PITCH = 480
NOTE_WIDTH = 360
NOTE_HEIGHT = 200
CARD_TOP = 260
ROW_GAP = 100
NOTE_PREFIX = "lab-stage-"


def graph_data(flow):
    return json.loads(flow["data"]) if isinstance(flow["data"], str) else flow["data"]


def node_kind(node):
    return node.get("data", {}).get("type", node.get("type"))


def card_size(node, measurements=None):
    measured = (measurements or {}).get(node["id"], {})
    # Reserve space for expanded forms, long titles and the description textarea.
    return float(measured.get("width", 360)), float(measured.get("height", 1200))


STAGES = {
    "chatInputComponent": ("Ask a question", "Start in Playground with one of the sample questions in the Agent description. The question travels to the right."),
    "chatOutputComponent": ("Read the answer", "The workflow returns its response here. Check the evidence, limitations and proposed human next step."),
    "SelectSqlQueryNode": ("Collect evidence", "Run the saved SELECT against the configured source. Preserve its row limits, dates and business scope."),
    "oraclePLSQLExecutor": ("Provide a tool", "Expose only the configured routine allowlist to the Agent on the right. A connection supplies a tool; the Agent decides when to call it."),
    "oracleDatabaseTools": ("Provide database tools", "The connected Agent uses this source to inspect permitted database evidence. Follow the source access and query limits."),
    "mcpServer": ("Inspect the Linux machine", "The connected Agent can call six read-only monitoring tools through the private MCP source. Inspect CPU, memory, filesystem usage, application health and recent activity."),
    "restAPITools": ("Provide API tools", "These environment-local REST sources supply tools to the Agent. Inspect each source's allowed operations and authentication before use."),
    "fileUpload": ("Read the handbook", "Upload the supplied document in this instance. Its text joins the user's question before the Agent answers."),
    "readCsv": ("Read the plan", "Load the supplied CSV. Keep illustrative planning data separate from the application evidence."),
    "currentDateTime": ("Add review time", "Supply the review timestamp. This does not make historical source records current."),
    "textCombiner": ("Join the context", "Combine the connected question, evidence or review time. Follow the wires to see which inputs reach the Agent."),
    "parser": ("Format the evidence", "Convert the upstream result into the bounded text used by the next stage. The saved parser does not expand the source scope."),
    "conditionComponent": ("Route the question", "The saved condition selects the appropriate branch. Read each branch from left to right; only the selected path answers."),
    "agentStep": ("Review and explain", "Use the configured model to interpret the connected context and tools. Agent description contains the purpose, boundaries and sample questions."),
}


def layout_graph(graph, measurements=None):
    """Return an idempotent, annotated DAG layout with all edges pointing right.

    Existing user notes survive. Invalid references and cycles fail before mutation.
    All processing nodes, tool edges and handles are preserved verbatim.
    """
    result = copy.deepcopy(graph)
    nodes = [n for n in result["nodes"] if n["type"] != "noteNode"]
    user_notes = [n for n in result["nodes"] if n["type"] == "noteNode" and not n["id"].startswith(NOTE_PREFIX)]
    by_id = {n["id"]: n for n in nodes}
    if len(by_id) != len(nodes):
        raise ValueError("Duplicate node IDs")
    parents = {key: set() for key in by_id}
    for edge in result["edges"]:
        if edge["source"] not in by_id or edge["target"] not in by_id:
            raise ValueError("Edge references a missing processing node")
        parents[edge["target"]].add(edge["source"])
    ranks = {}
    pending = list(by_id)
    while pending:
        ready = [key for key in pending if parents[key] <= ranks.keys()]
        if not ready:
            raise ValueError("Left-to-right layout requires an acyclic graph")
        for key in ready:
            ranks[key] = max([ranks[p] + 1 for p in parents[key]] or [0 if node_kind(by_id[key]) == "chatInputComponent" else 1])
            pending.remove(key)
    notes = []
    x = 0
    for column, rank in enumerate(sorted(set(ranks.values()))):
        members = [n for n in nodes if ranks[n["id"]] == rank]
        y = CARD_TOP
        kinds = list(dict.fromkeys(node_kind(n) for n in members))
        if len(kinds) == 1:
            title, explanation = STAGES.get(kinds[0], ("Process the context", "Follow the connected inputs into this stage, then continue to the right."))
        else:
            title, explanation = "Prepare the inputs", "These parallel sources provide evidence, tools or review time. Follow each connection to its consumer on the right."
        notes.append({
            "id": f"{NOTE_PREFIX}{column + 1}", "type": "noteNode",
            "position": {"x": x, "y": 0}, "width": NOTE_WIDTH, "height": NOTE_HEIGHT,
            "data": {"title": "Sticky Note", "description": "Workflow reading guide", "icon": "sticky-note",
                     "noteDetails": {"text": f"{column + 1}. {title}\n\n{explanation}", "backgroundColor": "rgb(255, 243, 163)", "textColor": "rgb(0,0,0)"}},
        })
        for node in members:
            node["position"] = {"x": x, "y": y}
            for field in ("width", "height", "measured", "initialWidth", "initialHeight", "selected", "dragging", "resizing"):
                node.pop(field, None)
            if "style" in node:
                for field in ("width", "height", "minWidth", "maxWidth", "minHeight", "maxHeight"):
                    node["style"].pop(field, None)
                if not node["style"]:
                    node.pop("style")
            y += card_size(node, measurements)[1] + ROW_GAP
        x += max(COLUMN_PITCH, max(card_size(n, measurements)[0] for n in members) + ROW_GAP)
    # Keep pre-existing annotations out of the newly arranged card area.
    x = 0
    for note in user_notes:
        note["position"] = {"x": x, "y": -float(note.get("height", NOTE_HEIGHT)) - ROW_GAP}
        x += max(COLUMN_PITCH, float(note.get("width", NOTE_WIDTH)) + ROW_GAP)
    result["nodes"] = nodes + user_notes + notes
    return result


def sample_questions(sample):
    special = {
        "adaptive-fulfillment-advisor": ["Can you check our backorders and tell me what we should tackle first?", "How did my earlier priority and donor-reserve corrections affect this recommendation?"],
        "fulfillment-memory": ["Which JDE environment is saved in my North America Fulfillment Standard? Answer from memory only; do not query JDE.", "Review active backorders using my saved recovery standard. Show the donor balance after the proposed allocation; do not change JDE."],
        "jps920-fulfillment-coach": ["Can you review today's backorders and tell me what we should tackle first?", "Explain which prior business corrections you applied and show the donor reserve arithmetic. Do not make JDE changes."],
    }
    questions = [step["text"] for session in sample["demo"]["sessions"] for step in session["steps"] if step["speaker"].lower() == "user"]
    limit = 6 if sample["slug"] == "linux-os-monitoring" else 2
    return special.get(sample["useCase"]["slug"], questions[:limit])


def describe_workflow(sample, graph):
    kinds = {node_kind(n) for n in graph["nodes"]}
    if "conditionComponent" in kinds:
        how = "Your question is routed by the saved condition to an outage or batch specialist, which uses its connected read-only source and returns a focused operations brief."
    elif sum(node_kind(n) == "agentStep" for n in graph["nodes"]) > 1:
        how = "The briefing Agent delegates to receivables and payables specialists. Each uses the shared read-only finance source, then the editor combines their findings into one response."
    elif "mcpServer" in kinds:
        how = "Your question and six curated MCP tools reach the Agent. It measures the Linux machine resources, checks application health, background jobs and osquery process evidence, reads bounded recent history when useful, and returns observations with timestamps, units and a human follow-up. The Agent recommends a human follow-up and changes nothing."
    elif "fileUpload" in kinds:
        how = "The uploaded handbook is combined with your question. The Agent answers from that text with section citations and identifies rules the handbook does not contain."
    elif "SelectSqlQueryNode" in kinds:
        how = "The saved bounded SELECT collects evidence. The workflow formats and combines it with your question" + (" and the review timestamp" if "currentDateTime" in kinds else "") + "; the Agent interprets that context and returns the answer."
        if "oraclePLSQLExecutor" in kinds:
            how += " The Agent can then call the allowlisted routine for the selected candidate."
        if "readCsv" in kinds:
            how += " The supplied fictional dispatch CSV is also included and remains distinct from the application records."
    else:
        how = "Your question reaches the Agent, which calls the connected " + ("REST APIs" if "restAPITools" in kinds else "allowlisted database tools") + " as needed, checks the returned evidence and produces the chat response."
    memory = sample.get("memory", {})
    if memory.get("mode") != "none":
        how += " Agent Memory recalls relevant user context and corrections across chats when enabled for this workflow."
    outcome = " ".join(sample["demo"]["expectedOutcomes"][:2])
    boundary = "Changes: read-only analysis; any drafts or recommendations require a human follow-up."
    if sample["useCase"]["slug"] == "invoice-review-actions":
        boundary = "Changes: this draft includes write-capable tools. It shows the exact invoice target and proposed values and requires explicit confirmation before a write. Authentication and action behavior need target-instance validation."
    return (sample["summary"] + "\n\nHow it works: " + how + "\n\nWhat you receive: " + outcome + "\n\n" + boundary +
            "\n\nSample questions:\n" + "\n".join("- " + q for q in sample_questions(sample)))


def prepare_workflow(flow, sample, model=LAB_MODEL, measurements=None):
    result = copy.deepcopy(flow)
    graph = graph_data(result)
    description = describe_workflow(sample, graph)
    # The catalog summary stays short; the Agent's multiline description contains
    # the full walkthrough and prompts. Neither requires a metadata API update.
    for node in graph["nodes"]:
        if node_kind(node) != "agentStep":
            continue
        template = node["data"]["template"]
        template["llmToUse"]["value"] = model
        title = node["data"].get("title", "Agent")
        role_description = description
        if sample["useCase"]["slug"] == "executive-operations-brief" and "specialist" in title.lower():
            topic = "receivables" if "receivables" in title.lower() else "payables"
            role_description = (f"{title}. Called by the executive briefing Agent to inspect bounded {topic} evidence through the connected read-only finance tools. "
                                "Keep organization, currency, actual source dates and sample limits explicit. Return observed facts, evidence gaps and a proposed human review step; do not infer a cash forecast or change records.\n\n"
                                f"Sample questions:\n- What {topic} evidence is available by organization and currency?\n- What should the finance owner verify before acting on this sample?")
        elif sample["useCase"]["slug"] == "it-operations-triage":
            topic = "outage" if "outage" in (node["id"] + title).lower() else "batch"
            role_description = (f"{title}. This is the {topic} branch selected by the upstream condition. Use only its connected read-only source; return dated observations, gaps and a concrete operator escalation step. "
                                "The sample does not prove end-to-end availability or authorize restarting, cancelling or administering anything.\n\nSample questions:\n" +
                                ("- Users cannot log in. What does the application-node evidence show?\n- Which additional checks must an operator make before declaring an outage?" if topic == "outage" else
                                 "- Review the latest concurrent requests and summarize batch follow-up.\n- Do the stored request times prove an SLA breach?"))
        field = template["agent_description"]
        field["value"] = role_description
        field["componentType"] = "textArea"
    laid_out = layout_graph(graph, measurements)
    result["data"] = json.dumps(laid_out) if isinstance(result["data"], str) else laid_out
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--model", default=LAB_MODEL)
    parser.add_argument("--measurements", type=Path,
                        help="Optional browser audit JSON with path and measured nodes for each workflow")
    args = parser.parse_args()
    measurements = {}
    if args.measurements:
        measurements = {item["path"]: {node["id"]: node for node in item["nodes"]}
                        for item in json.loads(args.measurements.read_text())}
    count = 0
    for manifest in sorted((args.root / "agents").glob("*/*/sample.json")):
        sample = json.loads(manifest.read_text())
        path = manifest.parent / sample["artifacts"]["workflow"]
        result = prepare_workflow(json.loads(path.read_text()), sample, args.model,
                                  measurements.get(manifest.parent.relative_to(args.root).as_posix()))
        path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        count += 1
    print(f"Prepared {count} native workflows for {args.model}")


if __name__ == "__main__":
    main()
