# Data Access and Data Handling Policy

## Purpose

This document defines the rules and expectations for accessing, storing, processing, sharing, and protecting company data and client data.

The purpose of this policy is to ensure that:
- sensitive data is protected
- access to data is controlled and justified
- data is stored in approved locations
- data is not shared inappropriately
- client data is handled responsibly
- test and production data are handled differently
- employees understand their responsibilities when working with data

This policy applies to all employees, contractors, and anyone who has access to company or client data.

## Scope

This policy applies to:
- client data
- internal company data
- financial data
- operational data
- employee data
- project data
- logs and system data
- backups
- exported data
- data stored in company systems
- data temporarily stored for analysis or development

This policy applies regardless of whether the data is stored:
- in company systems
- in cloud systems
- on company laptops
- in shared folders
- in development environments
- in testing environments
- in backups
- in exported files

This policy does not define:
- detailed infrastructure security architecture
- encryption standards in full
- legal data retention requirements for all jurisdictions
- client-specific contractual data rules
- incident response steps in full
- access provisioning procedures in full

Those topics may be covered by other policies such as the Security and Access Policy and Incident Management Procedure.

## Data classification

For the purpose of handling rules, data can be broadly classified into several categories.

### Public data

Public data is information that can be shared publicly without causing harm to the company or its clients.

Examples may include:
- public marketing materials
- public documentation
- publicly released reports
- job postings
- public website content

Public data has minimal handling restrictions, but employees should still avoid misrepresentation or accidental modification.

### Internal data

Internal data is information intended for company employees or contractors but not for public distribution.

Examples include:
- internal documentation
- internal procedures
- internal project documentation
- internal presentations
- internal dashboards
- non-public operational data

Internal data should not be shared outside the company without approval.

### Confidential data

Confidential data includes sensitive company or client information that could cause harm if disclosed.

Examples include:
- client data
- financial records
- contracts
- pricing information
- internal financial reports
- employee personal data
- security-related documentation
- internal system architecture details
- proprietary algorithms or models
- source code
- private datasets
- production system data

Confidential data must be protected and access must be limited to people with a business need.

### Highly sensitive data

Highly sensitive data includes data that could cause significant harm if exposed.

Examples may include:
- personal data protected by law
- authentication credentials
- private keys
- production database dumps
- full customer datasets
- security incident reports
- vulnerability information
- unannounced financial information
- merger or acquisition information

Highly sensitive data should be accessed only where strictly necessary and handled with additional care.

## Access to data

Access to data must follow the Security and Access Provisioning Policy.

In general:
- access must be based on business need
- access should follow least privilege
- access must be approved where required
- access should be removed when no longer needed
- production data access should not be granted by default
- access to client data should be limited to project team members or authorized personnel

Being an employee of the company does not automatically grant access to all internal or client data.

## Data storage locations

Company and client data should be stored only in approved storage locations.

Approved storage locations may include:
- company-managed cloud storage
- approved document management systems
- approved project repositories
- approved databases
- approved internal platforms
- approved backup systems

Company and client data should not be stored:
- in personal cloud storage accounts
- in personal email accounts
- on personal USB drives without approval
- in unmanaged personal folders
- on personal devices unless explicitly approved
- in public repositories unless approved and data is safe for public release

Temporary local storage on a company-managed laptop may be acceptable for operational work, but important data should be stored in approved central systems.

## Data sharing

Data sharing must be controlled and appropriate.

### Internal sharing

Internal sharing of internal or confidential data should be limited to people who need the data for their work.

Employees should avoid broadly sharing sensitive data in large communication channels where not necessary.

### External sharing

Sharing data outside the company should only happen where:
- there is a business reason
- sharing is allowed by contract or policy
- appropriate approval exists where required
- the recipient is authorized to receive the data
- sensitive data is protected appropriately

Employees should not send confidential or client data to external parties without authorization.

### Client data

Client data should only be shared:
- with the client
- with authorized project team members
- with approved subcontractors or partners where allowed
- through approved communication channels

Client data should not be used for unrelated projects or internal experiments without approval.

## Use of production data

Production data should be treated as sensitive.

In general:
- production data should not be copied into local environments unnecessarily
- production data should not be used in testing environments unless approved
- anonymized or test datasets should be used where possible
- production database dumps should be strictly controlled
- exporting large amounts of production data should require approval

If production data must be used for debugging or analysis, the scope should be limited and the data should be handled securely.

## Test data and development environments

Development and testing should use:
- synthetic data
- anonymized data
- test datasets
- sample datasets
- approved non-production datasets

Using real production data for testing should be avoided unless:
- there is a strong technical reason
- the data is properly protected
- the access is approved
- the data is removed after use where appropriate

Developers and analysts should assume that development environments are less secure than production and should avoid storing sensitive data there unnecessarily.

## Data retention and deletion

Data should not be kept longer than necessary for business or legal purposes.

Where possible:
- old temporary datasets should be deleted
- exported reports should not be stored indefinitely in random folders
- duplicate data copies should be minimized
- obsolete backups should be removed according to company practice
- project data should be archived or cleaned up after project completion where appropriate

This policy does not define exact retention periods for all data types but expects reasonable data hygiene.

## Exporting and downloading data

Exporting data from company systems should be done carefully.

Employees should avoid:
- exporting large datasets without reason
- storing exported data on unmanaged devices
- sending exported data via personal email
- storing exported data in public locations
- keeping old exported datasets indefinitely

If data must be exported for analysis or reporting, it should be stored in approved locations and deleted when no longer needed.

## Lost devices and data exposure

If a company device containing company or client data is lost or stolen, the employee must report it according to the Incident Management Procedure.

If data is accidentally shared with the wrong person or exposed inappropriately, this must also be reported.

Employees should not attempt to hide accidental data exposure incidents.

## Responsibilities

### Employees and contractors

All employees and contractors are responsible for:
- accessing only data they need
- storing data in approved locations
- not sharing sensitive data without authorization
- protecting company and client data
- reporting suspected data leaks or incidents
- deleting temporary data when no longer needed
- not copying data into personal storage
- not using client data for unrelated work

### Managers

Managers are responsible for:
- ensuring team members understand data handling expectations
- ensuring access requests are appropriate
- ensuring departing employees no longer have access to data
- ensuring project data is stored in appropriate locations

### IT and security roles

IT or security roles are responsible for:
- maintaining approved storage systems
- implementing access controls
- supporting backup and recovery systems
- assisting with access removal
- assisting with incident response where data exposure occurs

## Common mistakes to avoid

Common data handling mistakes include:
- storing client data locally and forgetting about it
- sharing confidential data in large chat channels
- using production data for testing without approval
- exporting data and leaving it in personal folders
- sending data to personal email
- uploading internal data to public repositories
- giving broad access to entire teams instead of specific people
- keeping old project data indefinitely in random locations

## Related documents

This policy should be read alongside:
- Security and Access Provisioning Policy
- Incident Management Procedure
- Project Kickoff Procedure
- Offboarding Policy

## Document limitations

This policy defines general data handling expectations but does not cover every technical control, legal requirement, or contractual data handling rule. Where client contracts or legal requirements impose stricter controls, those requirements take precedence.