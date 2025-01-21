# GymBookToStrong
Python script to parse the output of the GymBook application (https://www.gymbookapp.com/) into the output of the Strong application (https://www.strong.app/). This is also useful for Hevy (https://hevy.com/), which only allows the import of files exported by Strong

## How to Use

- Open and export CSV from GymBook
  - Go to Exports/Export/Record Data
  - Select CSV
- Launch Script passing as argument:
  - Input gymbook file
  - output location
- Open Hevy App and import file:
  - Go to Settings/Preferences/Export & Import Data/Import
  - Click on import
  - Select file

## Example of launch

```sh
python parse.py GymBook-Logs-2025-01-16.csv new_strong.csv
```