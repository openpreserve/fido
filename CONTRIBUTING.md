# Contributing

Thank you for considering a contribution to FIDO!
This document outlines the change submission process for FIDO, along with our standards for new code contributions.
Following these guidelines helps us assess your changes faster and makes it easier for us to merge your submission!

Contributions can be many things, including submitting bug reports, writing documentation or writing code which can be incorporated into FIDO.

The [Open Preserve Foundation (OPF)](http://openpreservation.org/) oversees the development of FIDO and appoints its maintainers.
If there should arise any debate or disagreement about what to merge or when, the OPF would be the final arbiter of that.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Submitting bugs](#submitting-bugs)
- [Submitting code changes](#submitting-code-changes)
- [Code Review & Approval](#code-review--approval)
- [Release process](#release-process)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Submitting bugs

FIDO uses GitHub Issues to track bugs.
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
We use GitHub pull requests for code review.
The checklist below contains some of our expectations, and will help you create a good pull request.

- New code should contributions should adhere to the [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/) and [PEP 257 -- Docstring Conventions](https://www.python.org/dev/peps/pep-0257/).
- Linebreaks should be used to limit line length within reason; we do not strictly enforce the 80-character line limit of PEP 8.
- Non-trivial changes should be accompanied by corresponding unit tests.
- FIDO runs on Python 2 and 3 (specifically versions 2.7, 3.4 and 3.5); changes must preserve this 2/3 compatibility.
- A pull request should resolve an existing GitHub issue and the name of its git branch should reference that issue by using the following naming convention: `dev/issue-<ISSUE_NO>-short-description`, e.g., `dev/issue-126-add-contributing-doc`.
- Git commits should be of a manageable size and should introduce one logical change; git commit messages should adhere to the [seven rules of a great Git commit message](https://chris.beams.io/posts/git-commit/):
  - Separate subject from body with a blank line
  - Limit the subject line to 50 characters
  - Capitalize the subject line
  - Do not end the subject line with a period
  - Use the imperative mood in the subject line
  - Wrap the body at 72 characters
  - Use the body to explain what and why vs. how

FIDO's Travis Continuous Integration configuration runs `pytest` to execute the tests, `flake8` to check PEP 8 conformance, and `pep257` to check PEP 257 (docstring) conformance.
You should run these tools locally before pushing a commit by running the following commands:

    $ python setup.py test
    $ flake8 --ignore=E501 ./fido
    $ pep257 --match='(?!fido).*\.py' ./fido


## Code Review & Approval

After a pull request is submitted, a maintainer will review the code for content, style & suitability of the new feature.
After the reviewer is satisfied with the changes, they will approve it on GitHub.
If at least one maintainer approves and there are no disapprovals for a week, the branch can be merged.
If the original committer is a maintainer, they can merge the branch.
For external contributors, a maintainer will merge the commits.


## Release process

A new release can happen when the maintainers decide enough changes have been merged, or when a new release of PRONOM happens.
To propose a release, a maintainer creates an issue with the release number and proposed release notes.
Discussion can happen in the release ticket about what outstanding pull requests could be merged.
If at least two maintainers approve and there are no disapprovals for a week, the release can be tagged and uploaded to PyPI.
The maintainer who proposed the release should do the tagging and uploading.
