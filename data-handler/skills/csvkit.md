# CSVKit

You can process CSV files using the `csvkit` tools.

## Commands

| Command | Description |
|---------|-------------|
| `csvlook` | Display CSV as a readable table |
| `csvstat` | Show statistics (min, max, mean, etc.) |
| `csvcut` | Select specific columns |
| `csvgrep` | Filter rows by pattern |
| `csvsort` | Sort by column |
| `csvjoin` | Join multiple CSV files |
| `csvsql` | Run SQL queries on CSV |

## Examples

```bash
# View CSV as table
csvlook data.csv

# Get statistics
csvstat data.csv

# Select columns 1 and 3
csvcut -c 1,3 data.csv

# Select by column name
csvcut -c name,email data.csv

# Filter rows where status is "active"
csvgrep -c status -m "active" data.csv

# Sort by amount descending
csvsort -c amount -r data.csv

# Run SQL query
csvsql --query "SELECT name, SUM(amount) FROM data GROUP BY name" data.csv
```
