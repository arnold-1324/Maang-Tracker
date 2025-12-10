# Excel Export Feature - Quick Start

## 🎯 What's New

You can now export **ALL** your database records to Excel format with a single click!

## 🚀 Quick Access

### Option 1: Browser (Easiest)
Just open this URL while your dashboard is running:
```
http://localhost:5100/api/export/excel
```

### Option 2: Command Line
```powershell
# Download using PowerShell
Invoke-WebRequest -Uri "http://localhost:5100/api/export/excel" -OutFile "my_export.xlsx"
```

### Option 3: Python Script
```powershell
# Run the standalone export script
.venv\Scripts\python.exe export_to_excel.py
```

## 📊 What Gets Exported

All database tables including:
- ✅ **users** - User accounts and profiles
- ✅ **user_progress** - Your learning progress
- ✅ **user_credentials** - Platform credentials
- ✅ **user_problem_status** - Problem-solving history
- ✅ **roadmap_topics** - Learning topics
- ✅ **topic_problems** - Practice problems
- ✅ **system_design_progress** - System design practice
- ✅ **weakness_analysis** - AI weakness analysis
- ✅ **user_focus** - Current focus areas
- ✅ **cache_store** - Application cache

## 📁 File Format

- **Format**: Excel (.xlsx)
- **Structure**: Multi-sheet workbook
  - First sheet: Summary with statistics
  - Other sheets: One per database table
- **Styling**: Professional headers, borders, auto-sized columns
- **Features**: Frozen headers, wrapped text

## 🔧 Files Created

1. **`export_to_excel.py`** - Standalone export script
2. **`test_export.py`** - Test the export functionality
3. **`EXPORT_GUIDE.md`** - Detailed documentation
4. **API Endpoint** - `/api/export/excel` in dashboard.py

## 🧪 Testing

Test if everything works:
```powershell
.venv\Scripts\python.exe test_export.py
```

## 📖 Full Documentation

See `EXPORT_GUIDE.md` for:
- Detailed usage instructions
- Troubleshooting guide
- Security considerations
- Use cases and tips

## ⚠️ Important Notes

1. **Server Must Be Running**: The dashboard server must be running on port 5100
2. **Database Location**: Uses the database at `./memory.db` (or `SQLITE_PATH` env var)
3. **Security**: The export contains sensitive data - keep it secure!
4. **File Size**: Export size depends on your data volume

## 🎨 Example Usage

```powershell
# 1. Make sure dashboard is running
# (Check if http://localhost:5100 is accessible)

# 2. Export via browser
# Open: http://localhost:5100/api/export/excel

# 3. Or use PowerShell
Invoke-WebRequest -Uri "http://localhost:5100/api/export/excel" -OutFile "backup_$(Get-Date -Format 'yyyyMMdd').xlsx"
```

## 🆘 Troubleshooting

**Problem**: "Connection refused"
- **Solution**: Start the dashboard server first

**Problem**: "Database not found"
- **Solution**: Check if `memory.db` exists in the project root

**Problem**: "Module not found: openpyxl"
- **Solution**: Run `.venv\Scripts\pip.exe install openpyxl`

---

**Need Help?** Check `EXPORT_GUIDE.md` for detailed documentation.
