# XRY Evidence Extractor
Script for extracting logical file system from .XRY container

![Demo](https://github.com/jankais3r/XRY-Evidence-Extractor/raw/main/demo.png)

### Features
- The script only extracts real files that were collected from the phone's file system, skipping items synthesized by XRY during decoding (e.g., embedded_SQLite_table_xxx files)
- The script encapsulates the files into a ZIP archive that protects the integrity of the evidence
- The script produces a log file with a detailed overview of which files were extracted and which ones were skipped (and why)

### Setup
- Place `Evidence_Exporter.py` into `%USERPROFILE%\Documents\XRY Python Scripts\`
- Open a case/collection in XAMN Elements
- Execute the script from XAMN's Scripts interface
- A ZIP archive with the evidence and a log file will be created on your Desktop

### Known limitations:
- ZIP archive cannot store Date Created, so only Date Modified metadata is preserved
- Only rudimentary support for Android's multi-volume images. More testing is needed.
- I wrote the script after playing around with XRY for 2 days, so it is very much possible that I got something wrong. For example, I tried to find a flag that would indicate whether a file is synthesized by XRY or coming straight from the phone's file system and I wasn't able to find such flag, so I had to come up with my own workaround to identify such files. I also could not find the case name exposed via the Python API, so I am naming the export with a current date, which is something I would like to change if possible.

MSAB Forum thread [here](https://forum.msab.com/viewtopic.php?id=2582)

### Changelog:
#### v0.4 - 2022-03-08 (commit [eb12d00](https://github.com/jankais3r/XRY-Evidence-Extractor/commit/eb12d00e5c4265ad3fdc900235d12a8a4a64b095))
- Added initial support for multi-volume images (e.g., Android)
- Added script's version number to the export filename for more transparent case tracking
- When parsing several particularly large cases, I encountered memory leak in XAMN, leading to OS crash after several hours. For this reason I re-introduced `Evidence_Exporter_perFileWrite.py` in v0.4. This is the old, much much slower approach where every file gets added to the ZIP separately. I do not recommend using this unless the regular script causes memory leaks for you.

#### v0.3 - 2022-02-25 (commit [7afb02c](https://github.com/jankais3r/XRY-Evidence-Extractor/commit/7afb02cdaa58236043f2c001ab5c0f75d22a183c))
- I found out that Python's `zipfile` module can't append files to an existing archive without re-reading and re-writing the whole archive. That lead to a needless wear on the SSD, as 50GB XRY image could produce over 2TB of read/write operations. I partially mitigated this by constructing the ZIP in memory and writing it to disk in batches. The batch size is dynamically determined based on the amount of free RAM. By default, the write gets triggered when the system has 3 GB of RAM left.
- Fixed a bug in the logging module resulting in some empty files having reported the size of the last non-empty file. This bug only affected the log file, not the actual ZIP.

#### v0.2 - 2022-02-24 (commit [926fe2a](https://github.com/jankais3r/XRY-Evidence-Extractor/commit/926fe2a895a95fa497c722b725adae8acaf334ca))
- Added en exception handling for encoding issues within the logging module

#### v0.1 - 2022-02-22 (commit [e057765](https://github.com/jankais3r/XRY-Evidence-Extractor/commit/e057765853c3ac1bc266a7f6e8ff30a0de854f6d))
- Initial release
