# Biomedical Waste Robot

A desktop app (Tkinter + MySQL) covering the full flow: robot waste
collection, compartment fill tracking, transport requests, QR-based
pickup/destination verification, disposal confirmation, alerts, complaints,
and an admin login gate.

Architecture follows a five-layer pattern:

```
models/   -> plain data classes
dao/      -> raw SQL, one class per table group
services/ -> business logic (validation, thresholds, alert-raising)
gui/      -> Tkinter windows, one file per screen
```

`services/simulation_service.py` fakes sensor/robot behaviour (waste
detection, movement, battery drain, random faults) since there's no physical
robot connected yet - swap it out later for a real hardware/API integration
without touching the GUI or DAO layers. Likewise, "scanning" a QR code
anywhere in this app means picking/typing a code in a text field, since
there's no camera/scanner hardware - `utils/qr_utils.py` is where you'd
plug in a real scanner later.

## Setup (Windows / PowerShell)

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Edit config/config.py with your MySQL username/password

# 3. Create the database and load the schema + seed data
python setup_db.py
```

`setup_db.py` uses the same `mysql-connector-python` driver the app already
depends on, so it works even if the `mysql` command-line client isn't
installed or isn't on your PATH. `database/schema.sql` drops and recreates
every table, so it's safe to re-run any time you want a clean slate.

```powershell
# 4. Run the app
python main.py
```

Log in with the seeded admin account: **admin / admin123**
(MD5-hashed for this demo only - swap for a real hashing scheme like bcrypt
before any real deployment.)

## The end-to-end flow this implements

```
Hospital bin -> Robot collection (auto or manual)
             -> Collection logged to MySQL, compartment fill updated
             -> Compartment reaches "full" -> Transport Request created
             -> Driver assigned -> Transport started
             -> Driver scans bin's QR (pickup)
                   match    -> access authorized, dumping confirmed
                   mismatch -> access denied, alert raised
             -> Driver scans destination's QR
                   match    -> destination verified
                   mismatch -> alert raised, disposal blocked
             -> Disposal confirmed -> compartment reset, transport completed
```

Every scan (pickup and destination, match or mismatch) is written to
`qr_verifications` and viewable in the **QR Verification Log** screen as an
audit trail.

## Screens

- **Login** - admin-only gate for the Dashboard; also has a no-login-required
  "Submit a Complaint" form for anyone to report a problem.
- **Dashboard** - summary counts + navigation (opens maximized).
- **Robot Status** - battery, status, current location per robot.
- **Waste Detection** - log a collection manually or simulate one.
- **Manual Collection** - dedicated fallback for when a robot has a
  technical issue: switch it to `manual` status and log its collections
  by hand until resolved.
- **Compartment Status** - fill-level bars per compartment.
- **Robot Tracking** - simple facility map showing robot locations.
- **Collection History** - full log of past collections.
- **Transport Requests** - request transport for a full compartment, assign
  a driver, start the transport.
- **Driver Scanner** - simulated pickup QR scan (match/mismatch).
- **Disposal Verification** - simulated destination QR scan + final
  disposal confirmation.
- **QR Verification Log** - read-only audit trail of every scan attempt.
- **Alerts** - active/resolved alerts (low battery, compartment full,
  malfunctions, QR mismatches), resolve or simulate new ones.
- **Complaints** (admin-only) - view and resolve complaints submitted from
  the login screen.

## Notes on a few small additions beyond a strict "one DAO per table" list

- `dao/admin_dao.py` + `models/admin.py` - needed so the login screen has a
  proper DAO/model instead of querying the `admin` table directly from the GUI.
- `dao/complaint_dao.py` + `models/complaint.py` - back the complaint form
  and the admin Complaints screen.
- Robot `status` gained a `manual` value (alongside idle/collecting/
  charging/error) to represent the technical-issue fallback mode.
