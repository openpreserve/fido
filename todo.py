#===============================================================================
# A python version of the Droid algorithm using the Droid Signature File
# 
# done. Evaluate current droid signatures to see which features are used
# done. Parse the sig file, building up an internal representation
# done. Match a sig against a string / byte array
# done. Move sig xml to conf
# done. Handle offset
# done. Offsets are 512, 4, 10 - so no long ones; use .{Offset}
# done. Match a sig against a file / stream
# done. Loop over sigs, find a match, report it
# done. Reuse buffer for start/end of small files
# done. Save parsed sig file and reload for increased speed
# done. Parse sig priority
# done. Parse formats with multiple signatures and multiple bytesequences (e.g. pdf/1.7 fmt/276)
# done. Replace ^ with /A and $ with /Z
# done. Handle one signature at a time, reading in the BOF and EOF into separate buffers.
# done. Why doesn't PDF 1.3 EOF match sample.  Because of eof v bof match behavior.
# done. Handle PositionType=Variable.  Variable means the sequence can be anywhere, i.e. .* prefix.
# done. Fix EOF matching!  'abc\Z' doesn't match 'xxxabcd', but '^ab' does match 'abxxx' But by starting with .*
# done. Sort formats by priority so that the first match is the best one.
# done. Add basic timing information. Running on sample directory at 60+ files/sec.
# done. Bug. didn't handle [a-b]{m,n] seen on c:\Documents and Settings\afarquha\My Documents\Meetings\2009\2009.05.25 IASSIST\iassist_v4_24b.mp3
# done. Do some profiling to see if it is worth doing any optimisation.  Not now. Memory usage is very low and stable for 2k files.  Speed is around 50 files/sec.  
# done. Handle zip.
# done. Handle multiple hits and removing lower priority items; RTF get 7 format matches; TIFF get 4.  Do the OBVIOUS fix and just remove-if.  Speed is OK for now.
# done. (I think) Check that offset/maxoffset are correctly handled
# done. Check the meaning of offset=0 with EOF.  Do we have any other than seqID=242
# done. droid recognises test.tar as a tarfile x-fmt/265. For pronom [a-z]{1-5} = [a-z].{1,5} !
# done. droid recognises buckland as html fmt/99; Incorrect handling of offset=0, maxoffset=n
# done. alani-* pdf not recognised.  Droid lists all pdf formats due to ext match.  Error in signature.
# done. v1.docx - fido sees zip, droid sees docx.  One signature looks for the ooxml indicator, the other for zip.  The zip signature differs from the real zip signature.  I think that the BOF should be EOF!
# done. ppt - fido  sees ole2, droid sees ppt.  The sig looks for a pattern that shows up at about 500kb, outside the default buffer.  Better to improve the signature.
# done. Test fidotests/corpus against droid results until they are the same.  They are correct, but not identical.
# done: Add more flexible output syntax (match droid?)
# done: Add timing to output at file, format, sig level.

# BUG: why are some files (always ppt?) so slow?  E.g. *v6B JM.ppt (might just be a bad signature)
#      When the bufsize goes from 7500 -> 7800, runtime goes from 100ms -> 20315ms!
#      Some bad non-linearity in the regex package
#      The offender appears to be FormatID=u'687',FormatName=u'MPEG 1/2 Audio Layer 3'
#      And other mpeg signatures.  They have multiple {36-1426} or so
# BUG: Need to be careful about SignatureName in print_times


# TODO: Add 
# TODO: Let prepare take xml from the zip.  This is to simplify distribution.
# TODO: Remove analysis from the distribution; create README.txt; add how-to
# TODO: Cleanup after zip properly.  We currently leave empty directories in the tempdir
# TODO: Rejig the file processing to us an iterator that could then read from a queue, stream, etc.
# TODO: Rejig the formats.py to implement a single function check_formats that is free to be optimsied.
# TODO: Add in some unittests
# TODO: Handle tar, jar, gzip container formats / transforms as in METS
# TODO: Introduce a lite syntax for signatures using just the needed information
# TODO: Load pronomlite and over-ride or extend the pronom info
# TODO: Handle end-tests efficiently.  Or review them for other optimisations. Reverse? s[::-1]
# TODO: Add a no EOF option (perhaps a bad idea until sigs are improved)
# TODO: Update file locations using conf
# TODO: Review api against jhove/2
# TODO: Review format information against FITS
# TODO: Add thread to handle signal and report on current file, #done, #todo, time
# TODO: Provide a files=- which reads the filenames from stdin
# TODO: Consider if we should use the non-greedy qualifiers *?, +?, ??, or {m,n}?; consider (?i)
# TODO: Rename _parse to _convert
# TODO: Get the magic file and add signatures from it
# TODO: Handle bigendian. x-fmt/392 JPEG2000 is the only one; consider reworking sig and dropping feature
# TODO: Improve some of the lousy signatures. E.g., for html, xml.
# TODO: Consider using mmap instead of reading the buffer
# TODO: Fix parseReport so that it doesn't create a new parser for each file.
# TODO: Skip zero-len files
# TODO: Thread/process so that recursive file find, file read, signature check can be done in parallel
# TODO: Try some alternate implementations of format checking.  E.g., no-compiled regex, try-me-else, first n-byte hash, reverse end
# TODO: Move the xml to a zip file.  Would be good, but there isn't a good way to get the items without creating the file.
# TODO: Move the fetch code into python
# TODO: Implement the signature fetch
# TODO: Produce a single file app / .exe
# TODO: Write up a series of blog posts, then a dlib article
# 
# PERFORMANCE
# on laptop, check(r'c:\Documents and Settings\afarquha\My Documents')
# - 7-10-2010 With check_sig call commented out, but with printing filenames in emacs buffer gives 6320 files in 101833.87ms, 62 files/sec
# - 7-10-2010 With no printing, 6320 files in 814.58ms, 7758 files/sec
# - 7-10-2010 With check_sig and printing,  6320 files in 101353.30ms, 62 files/sec
# - On the above, there are many no-matches; many pdf's, but lots of other stuff.
# 
# QUESTIONS
# - How can I get the string that r or b prefixes?  These are much more readable than repr(s).
# - How can I pickle the re.compile() results and the sig.py file
# - It looks as if there is only one pronom 'is subtype of' statement!
# 
# SIG NOTES
# - One of the PDFs ends with \n\r, instead of \r\n and the regex fails.  What is the right thing to do?  Change the regex to 'EOF..?. ?
# - One of the .mov files has ftypqt which is probably quicktime.  There is not signature for this! There is an mp4a at offset 591, 599.
# - The indirectoffset is not used
# - At least some of the variable patterns really seem to have bof+maxoffset nature
# - fmt/50 and fmt/51 (RTD) have identical signatures and no precedence.
# - zip x-fmt/263 and JAR x-fmt have no precedence relation.  But jar > zip 
# - JP2 in c:\Documents and Settings\afarquha\My Documents\DPT\Image Comparison\000833138_01_000021.jp2
# - Add signatures for: .txt, .sh, .css, .bib, .tex, .java, .py, .c, .dot (msft), .*~, .dot (graphs), Makefile, .bz2, .aspx, .js, .warc, .wgz, .xsd, .ini, .mm, .tab, 
# - Add signatures for: .azw .mbp (kindle), .itdb .itc2 (itunes), .ost, .bat, .sql, .eps, .sam, .ico
# - Review sigs for: .pdf (several fail), .htm, ~*.doc, .rtf, .mp3, .au, ~$....docx, .ps,
# - The sig for tar seems poor.  There are not separate sigs for the major tar formats (ustar, gnu, pax); it doesn't recognise my sample.
# - There isn't a sig for a tar.gz file, so it is just recognised as a gzip.
# - The docx signature has a BOF .* which should be a EOF, as it is in zip. If the BOF buffer is big enough, then it won't matter.
# - The ppt signature has a variable P.o.w.e.r. .P.o.i.n.t pattern that shows up in file rather late, after the buffer ends. Fido is OK.  Better to improve the sig.
# - The doc signature misses some of my documents, and treats them as ole2.  The doc signatures are not very good!
# - The doc signatures could have a EOF 'Microsoft Office Word Document\x00.*\Z' or similar
# 
# PYTHON NOTES
# - regex (?iLmsux) - (One or more letters from the set 'i', 'L', 'm', 's', 'u', 'x'.) 
#  The group matches the empty string; the letters set the corresponding flags:
#  re.I (ignore case), re.L (locale dependent), re.M (multi-line), re.S (dot matches all),
#  re.U (Unicode dependent), and re.X (verbose)
# 
# DROID NOTES
# - Droid produces a csv with columns:
#  "URI","FILE_PATH","NAME","METHOD","STATUS","SIZE","TYPE","EXT","LAST_MODIFIED","PUID","MIME_TYPE","FORMAT_NAME","FORMAT_VERSION"
# - zip items have a uri of zip:file:/file path!/zip path (but no File_PATH
# - The CONTAINER formats such as zip, jar, gzip are not specified as such in pronom, but only in the code.
# 
# TRANSLATION
# BOF -> \A  - better than ^
# EOF-> \Z   - better than $, which messes up with multiline
# ?? -> .?
# * -> .*
# {i} -> .{i}
# {i-j} -> .{i,j}
# {i-*} -> .{i,}
# [aa:bb] -> [aa-bb] - There are no [bbb:
# (abc|abc) -> (abc|abc) or (?:a|b)
# 
# Offset/Maxoffset
# .{Offset[,Maxoffset])
# 
# The following are define in the language, but never used
# [abc:abc] ->  - There are no [bbb: 
# [!a] -> [^a] - There are none
# [!abc] -> (?!abc) - There are none
# [!a:b] ->  - There are none
# Indirect offset
#===============================================================================
