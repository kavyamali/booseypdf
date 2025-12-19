# booseypdf
Downloads free, public online scores from boosey as PDF.

## Installation:

1. **Clone the repository:**

```
https://github.com/kavyamali/booseypdf.git
```
2. **In a terminal with python installed:**

```
pip install -r requirements.txt
```
3. **Login to Boosey in your browser, and download the html for the score in the same folder as ```main.py```.** **[LOGIN IS MANDATORY]**

   **For example:**
   ```
   https://www.boosey.com/cr/perusals/score?id=26174
   ```
4. **Run:**
```
python main.py "<filename>.html"
```
>The default html source is ```source.html```

Once downloaded, the PDF should be available in the same directory.

**Note:**
The html must be from a valid, logged in browser window, one that is not expired with its session.

## Advanced Options

You can customize the download using the following flags:

|Flag|Description|Example|
|-|-|-|
|`--file`| Path to the saved HTML file (optional if provided positionally)| `--file "score.html"`|
|`--res`| Image resolution: `_1` (Low), `_2` (Standard), `_3` (High), `_4` (Max)| `--res _4`|
|`--end`| Manually specify the end page number| `--end 20`|
|`--out`| Manually specify the output PDF filename|`--out "Final.pdf"`|

