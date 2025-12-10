# Database Export to Excel - User Guide

## Overview
You can now export all your MAANG Tracker database records to Excel format for easy viewing, analysis, and backup.

## Features
- ✅ Exports all database tables to a single Excel file
- ✅ Each table gets its own worksheet
- ✅ Professional formatting with headers and borders
- ✅ Auto-adjusted column widths
- ✅ Summary sheet with export statistics
- ✅ Frozen header rows for easy scrolling
- ✅ Timestamped filenames

## Database Tables Exported

The export includes all of the following tables:

1. **users** - User authentication and profile data
2. **user_progress** - Progress tracking on topics
3. **user_credentials** - Platform credentials (LeetCode, GitHub)
4. **user_problem_status** - Problem solving status and attempts
5. **user_focus** - Current focus topics
6. **roadmap_topics** - Available learning topics
7. **topic_problems** - Problems linked to topics
8. **system_design_progress** - System design practice progress
9. **weakness_analysis** - AI-generated weakness analysis
10. **cache_store** - Application cache data

## How to Export

### Method 1: Using the API Endpoint (Recommended)

Simply visit this URL in your browser while the dashboard is running:

```
http://localhost:5100/api/export/excel
```

This will automatically download an Excel file named `maang_tracker_export_YYYYMMDD_HHMMSS.xlsx`

### Method 2: Using the Python Script

Run the standalone export script:

```powershell
.venv\Scripts\python.exe export_to_excel.py
```

This will create an Excel file in the current directory.

### Method 3: Using cURL or PowerShell

**PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:5100/api/export/excel" -OutFile "maang_export.xlsx"
```

**cURL:**
```bash
curl -o maang_export.xlsx http://localhost:5100/api/export/excel
```

## Excel File Structure

The exported Excel file contains:

### Summary Sheet (First Tab)
- Export date and time
- Database path
- Total number of tables
- Total number of records
- Table-by-table record count

### Data Sheets
- One sheet per database table
- Column headers in blue with white text
- Bordered cells for easy reading
- Auto-adjusted column widths (max 50 characters)
- Frozen header row for scrolling

## Use Cases

1. **Data Backup** - Regular backups of your progress
2. **Data Analysis** - Analyze your learning patterns in Excel
3. **Progress Sharing** - Share your progress with mentors
4. **Data Migration** - Move data between systems
5. **Reporting** - Create custom reports and visualizations
6. **Auditing** - Review historical data and changes

## Tips

- **Regular Exports**: Export your data weekly for backup purposes
- **Compare Progress**: Export at different times to compare your progress
- **Data Analysis**: Use Excel's pivot tables and charts to analyze your learning patterns
- **Filter & Sort**: Use Excel's built-in features to filter and sort your data
- **Share Selectively**: You can delete sensitive sheets before sharing

## Troubleshooting

### "Database not found" error
- Ensure the dashboard is running
- Check that `memory.db` exists in the project root
- Verify the `SQLITE_PATH` environment variable

### "No tables found" error
- The database might be empty
- Run the initialization script first
- Check database permissions

### Download doesn't start
- Ensure the dashboard server is running on port 5100
- Check browser console for errors
- Try a different browser

## Security Note

⚠️ **Important**: The exported Excel file contains all your data including:
- User credentials (encrypted)
- Personal progress information
- Session tokens

**Keep the exported file secure and do not share it publicly!**

## Technical Details

- **Format**: XLSX (Excel 2007+)
- **Library**: openpyxl
- **Encoding**: UTF-8
- **Max Column Width**: 50 characters
- **Sheet Name Limit**: 31 characters (Excel limitation)

## Future Enhancements

Planned features for future versions:
- [ ] Selective table export
- [ ] Export to CSV format
- [ ] Export to JSON format
- [ ] Scheduled automatic exports
- [ ] Cloud backup integration
- [ ] Export filtering by date range
- [ ] Custom export templates

## Support

If you encounter any issues:
1. Check the console logs for error messages
2. Verify all dependencies are installed (`openpyxl`)
3. Ensure the database file is not locked by another process
4. Check file permissions in the export directory

---

**Last Updated**: December 2, 2025
**Version**: 1.0.0
