# Contract renewal demo flow

Open **EBS Contract Renewal with Document Evidence** and keep all steps in one saved conversation. The assistant uses model `AIW26-PAF-HOL6004-BOO6096`. Replace placeholders with values returned in that conversation. At step 5, replace `<your-email-address>` with the address you want to receive this draft's review; no recipient is preconfigured or taken from memory.

| Step | Say in chat | Expected result |
| --- | --- | --- |
| 1. Inspect | “Summarize my source BPA, supplier/site, dates and every current line price.” | Live EBS snapshot of the authorized agreement. |
| 2. Find evidence | “Find historical renewal evidence. Cite the documents and explain what terms are missing.” | Retrieved passages, citations and explicit evidence gaps. |
| 3. Propose | “Propose a 12-month renewal starting tomorrow with unchanged prices. Show all dates and old/new prices before staging.” | A proposal for inspection; no import. Confirm the exact dates shown. |
| 4. Stage | “Stage the proposal I just reviewed, validate it and show the draft ID and exact hash.” | An immutable, validated draft with a reproducible receipt. |
| 5. Request email | “Email review for draft <draft_id> to <your-email-address>.” | If the address is missing, the assistant asks for it before preparing or sending anything. With your address supplied, a readable text email preview and PAF's native Send/Cancel prompt appear. |
| 6. Send | `Send` | The email tool reports its actual sending result. Stop if it fails or remains pending. |
| 7. Review | After receiving and reviewing the email: “Approve draft <draft_id> with code 6004. Reason: I reviewed the dates, every line price and the evidence gaps.” | A review receipt for that exact hash, valid for one hour. |
| 8. Submit | In a separate message: “Submit reviewed draft <draft_id>.” | One Import Price Catalogs request. A request number alone means processing. |
| 9. Check | “Check draft <draft_id> again. Show its final status, request number, new BPA number and all imported line prices.” | `IMPORTED` and the resulting **Incomplete** BPA, or an honest pending/failure result. |
| 10. Verify in EBS | Open **Purchasing → Purchase Orders → Purchase Order Summary** in Oracle Forms and query the returned BPA number. | Inspect supplier/site, currency, dates, every line/item/UOM/price and **Incomplete** status. Final EBS approval remains a buyer action. |

At unchanged prices the new prices must match the live source snapshot exactly. Missing legal clauses remain gaps; historical purchasing PDFs do not establish legal approval.

The review request expires after 30 minutes. The known code `6004` demonstrates confirmation and is not proof of reviewer identity. Approval and import are separate actions.

The assistant reports a short email receipt rather than printing HTML, the tool JSON or a second copy of the email. PAF's built-in confirmation still previews the exact text before sending. If the database does not return `email_body_text`, stop and install the updated email helper; do not fall back to HTML or invent a replacement message.

For an already completed run, resume its conversation at **step 9**, then inspect its existing BPA in EBS. Do not submit again or create a second renewal merely to demonstrate the result. A fresh run creates a fresh agreement only after the user explicitly reviews and submits it.

Reopen the same saved conversation to show the proposal, validation, email confirmation/send result, later user approval, separate submission and final status receipt. If the import finishes after the first response, step 9 captures its final outcome in chat.
