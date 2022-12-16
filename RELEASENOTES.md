RELEASE NOTES
=============

Format Identification for Digital Objects (fido).
Copyright 2010 by Open Preservation Foundation.

Copyright 2010 The Open Preservation Foundation

Fido is made available under the Apache License, Version 2.0; see the file
LICENSE.txt for details.

Fido 1.6.0
-------------

2022-12-15

New command line options for updating signatures

- PRONOM signatures can now be updated from a web service [[#202][]].
- PRONOM v104 support with successful signature compilation (see issue [#203][]) [[#204][]].
- Closed issue [#100][], Added Unicode support for Windows Python 2.7 [[#200][]].
- Generated signature file now validated against XSD schema [[#197][]].
- Refactoring and cleared final PEP and FLAKE code lint warnings [[#197][]].
- Closed issue [#150][], trapped some of the signature compliation issues [[#197][]].
- Closed issue [#179][], [#198][]: Crash on XLS format by updating olefile version to 0.46 [[#195][]].
- Closed issue [#179][]: Crash on XLS format by updating olefile version to 0.46 [[#195][]].
- Closed issue [#192][]: Fixed signature file defaults [[#193][]].
- added update signature parameter to control signature download verison:
- trapped regex creation exception so that sig file creation is not derailed;
- PRONOM/DROID signature file now downloaded from URL rather than via SOAP service;
- moved sleep between SOAP downloads so that it's only applied between actual downloads, not when processing cached results;
- code style warnings:
  - some minor refactoring for complex methods;
  - factoring out string constants;
  - renamed some variables and methods;
  - removed some commented code;
  - tidied exit conditions; and
  - removed some unreachable code.

[#100]: https://github.com/openpreserve/fido/issues/100
[#150]: https://github.com/openpreserve/fido/issues/150
[#179]: https://github.com/openpreserve/fido/issues/179
[#192]: https://github.com/openpreserve/fido/issues/192
[#193]: https://github.com/openpreserve/fido/pull/193
[#195]: https://github.com/openpreserve/fido/pull/195
[#198]: https://github.com/openpreserve/fido/issues/198
[#200]: https://github.com/openpreserve/fido/pull/200
[#202]: https://github.com/openpreserve/fido/pull/202
[#203]: https://github.com/openpreserve/fido/issues/203
[#204]: https://github.com/openpreserve/fido/pull/204

Fido 1.4.0
-------------

2018-12-19

- Python 3 support [[#156][]]
- Update to PRONOM signatures v95 [[#159][]]
- Fixed bug with handling of embedded containers [[#164][]]
- Improvments to signature update code [#165][], [#167][]
- Code compliance with pytlint and PEP [[#161][], [#162][]]
- Minor bug fixes and typos [[#166][], [#170][], [#171][], [#172][], [#174][]]

[#156]: https://github.com/openpreserve/fido/pull/156
[#159]: https://github.com/openpreserve/fido/pull/159
[#161]: https://github.com/openpreserve/fido/pull/161
[#162]: https://github.com/openpreserve/fido/pull/162
[#164]: https://github.com/openpreserve/fido/pull/164
[#165]: https://github.com/openpreserve/fido/pull/165
[#166]: https://github.com/openpreserve/fido/pull/166
[#167]: https://github.com/openpreserve/fido/pull/167
[#170]: https://github.com/openpreserve/fido/pull/170
[#171]: https://github.com/openpreserve/fido/pull/171
[#172]: https://github.com/openpreserve/fido/pull/172
[#174]: https://github.com/openpreserve/fido/pull/174
