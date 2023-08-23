0001 Purpose of This Repo
#########################

Status
******

**Draft**

Context
*******

edX performs compliance with government regulations by checking users against the Consolidated Screening List provided by the U.S. Department of Commerce (SDN and ISN lists) on B2C single purchases and B2C subscription purchases. In the future, commerce-coordinator will also need access to this logic. This sanctions service will be used by multiple services, serving as a replacement for the SDN check and fallback that lives in ecommerce, which is deprecated.

Decision
********

We will create a repository that will facilitate SDN checks, maintain local backups of the SDN list, and record positive hits for reference.

Consequences
************

TODO: Add what other things will change as a result of creating this repo.

.. This section describes the resulting context, after applying the decision. All consequences should be listed here, not just the "positive" ones. A particular decision may have positive, negative, and neutral consequences, but all of them affect the team and project in the future.


References
**********

TODO: If applicable, add any references. If not applicable, remove section.

.. (Optional) List any additional references here that would be useful to the future reader. See `Documenting Architecture Decisions`_ and `OEP-19 on ADRs`_ for further input.

.. _Documenting Architecture Decisions: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
.. _OEP-19 on ADRs: https://open-edx-proposals.readthedocs.io/en/latest/best-practices/oep-0019-bp-developer-documentation.html#adrs
