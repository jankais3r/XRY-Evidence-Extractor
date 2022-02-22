# XRY Evidence Extractor


### Setup
- Place `Evidence_Exporter.py` into `%USERPROFILE%\Documents\XRY Python Scripts\`
- Open a case/collection in XAMN Elements
- Execute the script from XAMN's Scripts interface
- A ZIP archive with the evidence and a log file will be created on your Desktop

### Script's features
- Only extracting real files (skipping the ones synthesized by XRY during the Decoding phase)
- Encapsulating the files into a ZIP archive that protects the integrity of the evidence
- Produces a log file with detailed overview of which files were extracted and which ones were skipped (and why)

### Known limitations:
- ZIP format does not allow storing Date Created, so only Date Modified metadata are preserved
- I was only able to test this on an iPhone collection. If anyone has an Android collection they could test it on, I would appreciate any feedback or problems encountered
- I wrote the script after playing around with XRY for 2 days, so it is very much possible that I got something wrong. For example, I tried to find a flag that would indicate whether a file is synthesized by XRY or coming straight from the phone's file system and I wasn't able to find such flag, so I had to come up with my own workaround to identify such files. I also could not find the case name exposed via the Python API, so I am naming the export with a current date, which is something I would like to change if possible.

MSAB Forum thread [here](https://forum.msab.com/viewtopic.php?id=2582)
