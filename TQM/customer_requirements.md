# Customer Requirements

## Primary Customer

**Hospital Administration / Front Desk Staff**

Hospital administration is responsible for patient intake, appointment scheduling, and billing. They are the primary source of data entry and therefore the primary target of Q07 quality controls.

## Secondary Customers

- Attending Doctors — require accurate patient records and appointment history.
- Pharmacists — require accurate medicine stock information.
- Billing Staff — require correct patient and charge data.
- Hospital Management — require reliable audit trails and quality metrics.

## Customer Problems Identified

| # | Problem | Impact | Q07 Control |
|---|---|---|---|
| 1 | Phone numbers entered inconsistently | Emergency contact unreachable | Input Masking |
| 2 | Blood group typed as "B pos" instead of "B+" | Clinical risk | Dropdown Lists |
| 3 | Returning patient registered as new | Fragmented medical history | Auto-Complete |
| 4 | Staff accidentally deletes active patient record | Data loss | Confirmation Modals |
| 5 | Record changed without trace | Untraceable data error | Audit Logs |

## Voice of the Customer

| Customer Statement | CTQ |
|---|---|
| "I need to find the right patient quickly." | Auto-Complete search |
| "I should not be able to mistype a blood group." | Dropdown Lists |
| "Phone numbers must be in a consistent format." | Input Masking |
| "I want to know who changed a record and when." | Audit Logs |
| "I should not lose a record by clicking the wrong button." | Confirmation Modals |
