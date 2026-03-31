# Security and Access Provisioning Policy

## Purpose

This document defines the principles, responsibilities, and procedures for granting, modifying, reviewing, and removing access to company systems, data, and technical resources.

The objective of this policy is to ensure that access is provided in a controlled and auditable way, aligned with business need and security requirements. The policy is intended to reduce the risk of unauthorized access, excessive permissions, shared credentials, orphaned accounts, and inconsistent access decisions across teams.

A well-functioning access management process should ensure that:
- each user has only the access needed for their role
- sensitive or privileged access is subject to additional scrutiny
- access changes are traceable to a request and business justification
- access is reviewed on a recurring basis
- access is removed promptly when no longer needed
- onboarding and offboarding are supported without bypassing security principles

This document should be used by managers, IT, system owners, and any employee requesting or approving access.

## Scope

This policy applies to:
- full-time employees
- part-time employees
- contractors and consultants
- interns or temporary workers
- any other individual receiving access to company-managed systems

This policy applies to access for:
- email and communication tools
- document storage and collaboration platforms
- issue tracking and project tools
- internal business systems
- development environments
- client-connected systems where the company is responsible for account provisioning
- VPN and remote access tools
- shared internal platforms administered by the company

This policy does not define:
- detailed password composition rules for every tool
- physical office security procedures in full
- network architecture standards
- software development secure coding standards
- data retention rules
- equipment return logistics

Those topics may be covered by separate documents or operating procedures.

## Core principles

### Least privilege

Access must follow the principle of least privilege. Users should receive only the minimum level of access required to perform their current responsibilities.

Access should not be granted for convenience, future possible need, or because another user already has similar access.

### Business need

Every access request must have a valid business reason. Access should be connected to:
- a defined role
- a project assignment
- a support responsibility
- an approved operational need
- a temporary task with defined duration, where applicable

### Named accounts only

Each user must use their own named account wherever the system supports it. Shared accounts are not allowed unless there is a documented technical exception approved by the responsible owner.

Where shared or service-style credentials cannot be avoided for technical reasons, access to those credentials should still be restricted and controlled through a defined process.

### Separation of standard and privileged access

Standard role-based access is not the same as privileged, administrative, or production access.

The fact that a user is onboarded into a team does not mean they should automatically receive:
- production access
- administrator permissions
- unrestricted data access
- access to client-sensitive environments
- security administration capabilities

Such access must be separately requested and approved.

### Timely removal of access

Access must be removed when:
- a user leaves the company
- a contractor engagement ends
- a role changes and access is no longer needed
- temporary access expires
- a system owner or manager determines that business need no longer exists

### Traceability

Access decisions should be traceable to a request, approval, or defined role profile. It should be possible to explain:
- who requested the access
- why it was requested
- who approved it
- when it was granted
- whether it was time-limited

## Roles and responsibilities

### HR

HR is responsible for providing start-date and end-date information relevant to access lifecycle events. HR typically:
- notifies relevant parties when onboarding starts
- confirms final working day for offboarding
- informs IT and the manager when a person is joining or leaving

HR does not approve technical access in place of a manager or system owner unless explicitly authorized to do so by internal procedure.

### Hiring manager or line manager

The manager is responsible for ensuring that requested access is appropriate for the person’s role and current responsibilities.

The manager must:
- request standard access needed for the role
- provide business justification where required
- avoid over-requesting permissions
- review access when prompted
- inform IT or the relevant process owner when access is no longer needed
- support timely offboarding actions

Managers are also responsible for ensuring that production or sensitive-system access is only requested where genuinely necessary.

### IT or internal operations

IT is responsible for provisioning standard accounts and implementing access changes within the systems under its administration or control.

IT may:
- create accounts
- assign standard access groups
- configure devices and baseline settings
- disable accounts
- remove access as instructed through the approved process

IT should not independently grant non-standard privileged access without the required approvals, except where emergency procedures explicitly allow it.

### System owners

System owners are responsible for approving or rejecting access to systems under their authority, especially where access is privileged, production-related, client-sensitive, or operationally critical.

System owners should ensure that:
- access is aligned with business need
- the requested level of permission is appropriate
- temporary access is limited in time where possible
- periodic reviews are conducted when applicable

### Individual users

Users are responsible for:
- using only their own assigned accounts
- protecting authentication credentials
- completing required security steps such as MFA where supported
- reporting access problems or suspected misuse
- not attempting to obtain unauthorized access
- not sharing accounts or passwords

## Access categories

For practical purposes, access can be grouped into the following categories.

### Standard role-based access

This includes access commonly required by most employees or most members of a given team, such as:
- company email
- chat tools
- document storage
- internal knowledge base
- issue tracking tools
- time tracking or administrative tools where relevant

Standard access may be provisioned through predefined onboarding profiles or groups where those exist.

### Team-specific operational access

This includes access needed by a specific function or team, such as:
- engineering repositories
- finance systems
- project management workspaces
- internal dashboards
- support tools

This access still requires business need, but may often follow common patterns for a function.

### Sensitive data access

This includes access to data or systems containing:
- financial records
- personal data
- client-confidential materials
- security-relevant logs or administrative records
- operational systems with material business impact

Such access should be more carefully reviewed and should not be assumed from job title alone.

### Privileged or administrative access

This includes:
- administrator rights
- production environment access
- database administration permissions
- security configuration permissions
- infrastructure management rights
- elevated access that can materially affect availability, integrity, or confidentiality

Privileged access must always be separately requested and approved.

### Temporary access

Temporary access may be granted for:
- incident response
- short-term project work
- troubleshooting
- migration activities
- coverage during absence of another employee

Where temporary access is granted, the request should state the expected duration or review point.

## Onboarding-related access

During onboarding, users may receive standard access appropriate to their role. This commonly includes:
- email
- chat
- document storage
- issue tracking
- standard internal collaboration tools

Standard onboarding does not automatically include privileged access, production access, or unrestricted access to sensitive client or financial data.

If a new joiner requires special access from day one, the request should be submitted in advance and include sufficient justification. Some access may depend on additional approvals, project assignment confirmation, or a security review.

Multi-factor authentication is required for all company accounts that support it. New joiners are expected to activate MFA during the first week unless a more specific deadline is defined for a given system.

## Access request process

### Required request information

Access requests should contain enough information to allow the approver to make a reasonable decision. At minimum, requests should include:
- employee or contractor name
- manager name
- system or systems requested
- requested level of access
- business justification
- duration, if temporary
- project or client context, if relevant

Requests missing key information may be returned for clarification.

### Standard requests

Standard requests may be fulfilled by IT or operations using predefined role profiles or groups, provided the request is consistent with the person’s role and does not involve unusual privilege.

### Non-standard requests

Non-standard requests, including privileged access or access to highly sensitive systems, require explicit approval by the relevant system owner, responsible manager, or other designated approver.

Examples of non-standard requests include:
- production access for engineers
- finance system access for a non-finance role
- administrative rights
- access to client systems containing sensitive data
- temporary high-privilege access for troubleshooting

### Temporary access handling

Where possible, temporary access should have:
- a defined start point
- a defined end point
- a review point
- a clear reason for the temporary elevation

Temporary access should not silently become permanent through inaction.

## Approval expectations

Approval should be proportionate to the sensitivity of the requested access.

As a general principle:
- standard access may be approved through normal managerial request and role-based provisioning
- sensitive or non-standard access should be approved by the relevant owner
- privileged or production access should require explicit owner approval and should not be assumed from team membership

Approval should be based on current job need, not anticipated future need.

## Production access

Production access is treated separately because of its operational and security significance.

Production access:
- is never granted automatically during onboarding
- must be separately requested
- must include a business reason
- should be limited to the minimum level needed
- may be restricted to certain personnel or teams
- may be time-limited where full standing access is not necessary

Being part of an engineering, data, or operations team does not by itself justify broad production access.

Where feasible, read-only access, limited-scope access, or time-bound access should be preferred over broad standing permissions.

## Access reviews

Managers should review team access rights at least once every quarter.

The purpose of access review is to identify:
- access no longer needed
- excessive permissions
- users who changed role
- temporary access that should be removed
- accounts that appear inactive or unusual
- mismatches between role and actual access

System owners may run more targeted reviews for high-risk systems.

Access review should not be treated as a purely administrative exercise. If a reviewer cannot explain why access exists, it should be investigated.

## Changes in role or assignment

When a user changes team, role, or project assignment, access should be reassessed. This may include:
- granting newly required access
- removing access no longer needed
- changing level of privilege
- ending project-specific access
- requesting new approvals where the new role requires sensitive systems

Access should evolve with the role; it should not accumulate indefinitely.

## Offboarding and access removal

When a person leaves the company or their engagement ends, access removal should happen promptly and in coordination with HR, the manager, and IT.

At minimum:
- HR communicates the final working day
- the manager identifies systems and any special cases
- IT disables the relevant accounts
- VPN, email, and internal tools must be disabled
- badges and physical access should be revoked where applicable
- access to critical systems may be removed earlier if necessary

Unless otherwise specified by internal procedure or legal requirement, account deactivation should happen by the end of the employee’s last working day.

In some situations, earlier access removal may be appropriate, such as:
- involuntary departure
- elevated security concern
- access to particularly sensitive systems
- immediate reassignment of critical duties

This policy addresses digital access removal only. Physical equipment return is covered in the Offboarding Policy.

## Devices and endpoint security

Company laptops and managed devices used for company access must use:
- disk encryption where supported
- approved endpoint protection
- baseline security settings defined by IT

Users should not disable or circumvent these controls without authorization.

Granting a user account does not remove the requirement to secure the endpoint through which that account is used.

## Exceptions

Exceptions to this policy should be limited and should only be made where there is a documented operational need and compensating controls are considered.

Examples of possible exceptions may include:
- technical limitations in a legacy system
- urgent incident response
- temporary vendor access with constrained scope
- controlled use of a non-standard account model in a specific environment

An exception should not become the default way of working.

## Common prohibited practices

The following practices are not allowed under normal circumstances:
- sharing named accounts
- granting admin rights because they are “easier”
- keeping access after a person has changed role without review
- granting production access by default during onboarding
- requesting broad access without business justification
- using personal accounts instead of company-managed accounts for internal systems where managed accounts are required

## Minimum completion criteria for an access lifecycle event

### For granting access
An access request is considered properly completed when:
- the request identifies the user and system
- business need is stated
- required approvals are obtained
- access is provisioned at the correct level
- the user can authenticate securely
- MFA is enabled where supported and required

### For removing access
An access removal event is considered properly completed when:
- the relevant accounts are disabled or removed
- remote access is disabled where applicable
- critical or privileged access is removed
- the responsible parties have been informed
- any time-limited or project-specific access is also closed where appropriate

## Related documents

This policy should be read alongside:
- HR Onboarding Policy
- Employee Offboarding Policy
- any system-specific operating procedures where applicable

## Document limitations

This policy defines the control framework for access decisions and lifecycle handling. It is not a complete technical standard for identity architecture, logging, or security engineering, and it does not replace more detailed procedures that may exist for specific systems or environments.