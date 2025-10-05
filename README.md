# Remote Patient Monitoring DataHub

A Django-based API for managing users, organizations, clinician onboarding, and patient registrations for a Remote Patient Monitoring platform.

### Prerequisites
- Docker and Docker Compose installed
- Python 3.12 (only needed if running locally outside Docker)
- Postman (recommended) or any HTTP client

## 1) Configure local environment variables

This project reads the Django `SECRET_KEY` from an environment file.

1. Create a `.env` file at the repository root with at least the following content:
```
SECRET_KEY=replace-with-a-long-random-secret
```

Notes:
- The Django settings read `SECRET_KEY` from environment: see `rpm_datahub/settings.py`.
- The Docker Compose service automatically loads `.env`.

### Generate a strong SECRET_KEY
Use either command:
```bash
python -c 'import secrets; print(secrets.token_urlsafe(64))'
```
or:
```bash
openssl rand -base64 64
```

Then set in `.env`:
```bash
SECRET_KEY="paste-the-generated-value-here"
```

## 2) Run the project with Docker Compose

From the repository root, build and start the API:
```
docker compose up --build
```

The API will be available at:
- Base URL: `http://localhost:8000/`
- Admin site: `http://localhost:8000/admin/`

The container mounts the project directory for live-reload-like development (Django dev server).

## 3) Testing with Postman (recommended)

Import/create a Postman collection with these base settings:
- Base URL variable: `{{base_url}}` = `http://localhost:8000`
- For authenticated endpoints, use Bearer token from JWT login (`/auth/login/`).

## API Overview (key endpoints)

Namespaces:
- Accounts/Auth: `{{base_url}}/auth/`
- Organizations: `{{base_url}}/organizations/`
 - Patients: `{{base_url}}/patients/`
 - Observations: `{{base_url}}/observations/`

Accounts/Auth endpoints:
- `POST /auth/patient/` — Register a patient user (no auth required)
- `POST /auth/login/` — Obtain JWT access/refresh tokens
- `POST /auth/token/refresh/` — Refresh access token
- `GET /auth/me/` — Get current user (auth required)
- `GET /auth/login-attempts/` — List login attempts (admin only)
- `GET /auth/clinician-profile/` — Retrieve current clinician profile (clinician auth)
- `POST /auth/clinician-profile/` — Create clinician profile (clinician auth)
- `PUT/PATCH /auth/clinician-profile/{clinician_profile_id}/` — Update clinician profile (admin or org admin)
- `POST /auth/clinician-profile/{clinician_profile_id}/verify/` — Verify clinician profile (admin or org admin)

Organization endpoints:
- `GET/POST /organizations/` — List or create organizations (admin only)
- `GET /organizations/{organization_id}/` — Retrieve organization (admin or org admin)
- `PUT/PATCH /organizations/{organization_id}/` — Update organization (admin or org admin)
- `DELETE /organizations/{organization_id}/` — Delete organization (admin only)
- `GET/POST /organizations/{organization_id}/admins/` — List/create organization admin (admin or org admin)
- `GET /organizations/{organization_id}/clinician-profiles/` — List clinician profiles for org (admin or org admin)
- `GET /organizations/{organization_id}/members/` — List members (admin or org admin)
- `GET/PUT/PATCH /organizations/{organization_id}/members/{membership_id}/` — Retrieve/update member (admin or org admin)
- `POST /organizations/{organization_id}/members/{membership_id}/approve/` — Approve clinician membership (org admin)
- `POST /organizations/{organization_id}/patient-consent/` — Patient grants consent from org to access its data(patient auth)
- `GET/POST /organizations/{organization_id}/invitations/` — List/create clinician invitations (org admin)
- `POST /organizations/invitations/{invitation_token}/accept/` — Accept invitation (public)

## 4) Register a patient user

Endpoint:
- `POST {{base_url}}/auth/patient/`

Example JSON payload:
```json
{
  "email": "patient1@example.com",
  "password": "StrongPassword123!"
}
```

Expected:
- 201 Created with user data. The account role is `patient` and the user is active.

Notes:
- This creates a login-capable user but not a patient profile. See section 6.

## 5) Clinician onboarding workflow

High-level steps:
1. Admin user creates an organization
2. Admin user creates an organization admin
3. Organization admin sends an invitation to a clinician (requires clinician email)
4. Clinician accepts invitation (creates user if needed and a pending org membership)
5. Clinician logs in and creates a clinician profile
6. Organization admin verifies the clinician profile
7. Organization admin approves the membership (requires verified profile)

Detailed steps with endpoints and example payloads:

### 5.1 Create an organization (admin)
- `POST {{base_url}}/organizations/`
- Auth: Admin JWT

Example payload:
```json
{
  "name": "Acme Health",
  "address": "123 Main St, Springfield",
  "contact_number": "+1-555-123-4567",
  "description": "Primary care network",
  "organization_type": "clinic",
}
```

Response includes `organization_id`.

### 5.2 Create an organization admin (admin or org admin)
- `POST {{base_url}}/organizations/{organization_id}/admins/`
- Auth: Admin JWT (or org admin)

Example payload (creates user if email not found):
```json
{
  "email": "orgadmin@example.com",
  "password": "StrongPassword123!"
}
```

Creates/ensures an active membership with role `admin` for this organization.

### 5.3 Send invitation to clinician (org admin)
- `POST {{base_url}}/organizations/{organization_id}/invitations/`
- Auth: Org Admin JWT

Example payload:
```json
{
  "invitee_email": "clinician1@example.com"
}
```

Notes:
- Fails if a pending, unexpired invitation already exists or if the clinician already has active/pending membership.
- A mock email is “sent” by writing the accept URL to a file under `/app/invitations/` inside the container.

### 5.4 Accept invitation (public)
- `POST {{base_url}}/organizations/invitations/{invitation_token}/accept/`
- Auth: None

Payloads:
- If the clinician does not have an account yet, include a password:
```json
{
  "password": "StrongPassword123!"
}
```
- If the clinician already has an account, you can POST an empty JSON object `{}`.

Effects:
- Creates user (role `clinician`) if not exists.
- Creates an organization membership with role `member` and status `pending`.

### 5.5 Clinician logs in and creates a clinician profile
1) Login to obtain JWT tokens
- `POST {{base_url}}/auth/login/`
```json
{
  "email": "clinician1@example.com",
  "password": "StrongPassword123!"
}
```
- Save the `access` token for subsequent requests.

2) Create clinician profile (clinician auth)
- `POST {{base_url}}/auth/clinician-profile/`
```json
{
  "first_name": "Alex",
  "last_name": "Smith",
  "npi_number": "1234567890",
  "medical_license_number": "A1234567",
  "license_state": "CA",
  "license_expiration_date": "2027-12-31",
  "specialty": "Cardiology"
}
```

3) Retrieve profile (optional)
- `GET {{base_url}}/auth/clinician-profile/`

### 5.6 Verify clinician profile (admin or org admin)
- `POST {{base_url}}/auth/clinician-profile/{clinician_profile_id}/verify/`
- Auth: Admin or Org Admin (who is admin for an org where the clinician is a member)

No payload required. Response includes the updated profile with `credentials_verified: true`.

### 5.7 Approve clinician membership (org admin)
- `POST {{base_url}}/organizations/{organization_id}/members/{membership_id}/approve/`
- Auth: Org Admin

Notes:
- Requires the clinician profile to exist and be verified.
- Membership must currently be `pending`.

## 6) Patients app endpoints and patient profile

After registering and logging in as a patient, create your patient profile.

Endpoints (Patients app):
- `POST {{base_url}}/patients/` — Create patient profile for the current user
- `GET/PUT/PATCH {{base_url}}/patients/me/` — Retrieve/update your patient profile

Auth: Patient JWT

Example payload for `POST /patients/`:
```json
{
  "first_name": "Taylor",
  "last_name": "Lee",
  "date_of_birth": "1980-05-20",
  "gender": "female",
  "contact_number": "+1-555-222-3333",
  "address": "456 Oak Ave, Springfield"
}
```

Expected:
- 201 Created with `patient_id` and profile fields. The `user` field is set automatically.

## 7) Patient consent to organizations

Patients must grant consent to an organization before the organization can assign clinicians to their care team or clinicians can access their data.

Endpoint (Organizations app):
- `POST {{base_url}}/organizations/{organization_id}/patient-consent/`

Auth: Patient JWT

Payload:
- You can POST an empty JSON object `{}`. The server sets `patient` and `organization` automatically, with defaults:
  - `consented_at`: now
  - `expires_at`: 365 days from creation

Notes:
- `organization_id` is the UUID of the organization.
- Consent is required before an org-admin can assign clinicians to the patient’s care team.

## 8) Care team memberships (assign clinicians to a patient)

Base path is under Organizations: `{{base_url}}/organizations/{organization_id}/patients/{patient_id}/careteam-memberships/`

Endpoints (CareTeamMemberships app):
- `GET /organizations/{organization_id}/patients/{patient_id}/careteam-memberships/` — List care team memberships (auth: org admin or clinician for patient)
- `POST /organizations/{organization_id}/patients/{patient_id}/careteam-memberships/` — Create care team membership (auth: org admin)
- `GET /organizations/{organization_id}/patients/{patient_id}/careteam-memberships/{membership_id}/` — Retrieve membership (auth: org admin or clinician for patient)
- `POST /organizations/{organization_id}/patients/{patient_id}/careteam-memberships/{membership_id}/deactivate/` — Deactivate membership (auth: org admin)

Prerequisites for creating a care team membership:
- The patient has a patient profile (`POST /patients/`).
- The patient has granted consent to the organization (`POST /organizations/{organization_id}/patient-consent/`).

Example payload for creating a care team membership:
```json
{
  "clinician": "<clinician_profile_uuid>",
  "role": "primary care physician",
  "reason_for_assignment": "Chronic condition management"
}
```

Server-managed fields:
- `status` is set to `active` on creation.
- `patient`, `managing_organization`, `assigned_by` are populated by the server.

## 9) Observations endpoints

There are separate endpoints for patients (self-service) and clinicians (accessing a patient’s data when permitted):

- Patient endpoints (Observations app, auth: patient)
  - `GET /observations/` — List your observations
  - `POST /observations/` — Create a new observation for yourself
  - `GET /observations/{observation_id}/` — Retrieve one of your observations

- Clinician endpoints (Patients app, auth: clinician with access)
  - `GET /patients/{patient_id}/observations/` — List observations for a patient
  - `GET /patients/{patient_id}/observations/{observation_id}/` — Retrieve observation for a patient

Notes:
- Clinician access requires a valid clinician-patient relationship and organizational context as enforced by permissions.

## Authentication flow (JWT)
- Login: `POST /auth/login/` → returns `access` and `refresh` tokens
- Refresh: `POST /auth/token/refresh/` → returns a new `access` token
- Include header: `Authorization: Bearer <access_token>`

## Development notes
- Default DB: SQLite (`db.sqlite3`)
- Custom user model: `accounts.RpmUser` (email as username, roles: admin/clinician/patient)
- Permissions enforce admin/org-admin/clinician flows as described by endpoints

## Troubleshooting
- 403 errors: Ensure correct role and token; verify org-admin permissions for the target organization
- 400/409 on invitations: Invitation already exists or membership already exists
- 400 on membership approval: Verify clinician profile is verified and membership is pending
- SECRET_KEY missing: Ensure `.env` exists with `SECRET_KEY=...` and container restarted
