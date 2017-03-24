# Contributing

Thank you for considering a contribution to FIDO!
This document outlines the change submission process for FIDO, along with our standards for new code contributions.
Following these guidelines helps us assess your changes faster and makes it easier for us to merge you submission!

Contributions can be many things, including submitting bug reports, writing documentation or writing code which can be incorporated into FIDO.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Submitting bugs](#submitting-bugs)
- [Submitting code changes](#submitting-code-changes)
- [Code Review & Approval](#code-review-&-approval)
- [Release process](#release-process)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Submitting bugs

FIDO uses Github Issues to track bugs.
If you find a problem, please check existing bugs before submitting your issue.

Useful questions to answer if you're having problems include:

* What version of FIDO are you using?
* How was FIDO installed? Via pip, manually using a git checkout, etc.
* What did you do to cause this bug to happen?
* What did you expect to happen?
* What did you see instead?
* Can you reproduce this reliably?


## Submitting code changes

Every new feature and bugfix is expected to go through code review before inclusion.
We use Github pull requests for code review.


## Code Review & Approval

After a pull request is submitted, a maintainer will review the code for content, style & suitability of the new feature.
After the reviewer is satisfied with the changes, they will approve it on Github.
If at least two maintainers approve and there are no disapprovals for a week, the branch can be merged.
If the original committer is a maintainer, they can merged the branch.
For external contributors, a maintainer wire merge the commits.


## Release process

A new release can happen when the maintainers decide enough changes have been merged, or when a new release of PRONOM happens.
To propose a release, a maintainer creates an issue with the release number and proposed release notes.
Discussion can happen in the release ticket about what outstanding pull requests could be merged.
If at least two maintainers approve and there are no disapprovals for a week, the release can be tagged and uploaded to PyPI.
The maintainer who proposed the release should do the tagging and uploading.
